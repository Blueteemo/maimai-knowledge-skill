#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键同步舞萌DX国服知识库。

数据优先级：
1. 国服曲目 / 分类 / 版本 / 显示等级：CrazyKidCN/maimaiDX-CN-songs-database
2. ID / 定数 / 谱师 / 音符数：Diving-Fish /music_data（无需 Developer-Token）
3. 别名：YuzuChan alias API
4. Diving-Fish 暂时不可用时：Choimoe/dxdataViewer sheets.csv 作为谱面元数据备用源

原则：
- 国服显示等级永远以国服曲库为准。
- 精确定数 ds 只有在能与当前国服显示等级安全对应时才写入；否则写 null。
- 谱面特征 chart_tags 不是实时 API 数据，更新时保留仓库已有标签。
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

ROOT = Path(__file__).resolve().parents[1]
LEVEL_INDEX = ROOT / "level_index.json"
KB_DIR = ROOT / "knowledge_base"
SONGS_FILE = ROOT / "songs.json"
TITLE_EQUIVALENTS = {"Link(CoF)": "Link"}


def identity(title: str, artist: str) -> Tuple[str, str]:
    return title_norm(TITLE_EQUIVALENTS.get(title, title)), norm(artist)


def load_annotations() -> Dict[Tuple[str, str], Dict[str, Any]]:
    """旧 Markdown 的标签未区分 SD/DX；只保留在歌曲层，不能猜测谱面归属。"""
    if SONGS_FILE.exists():
        songs = json.loads(SONGS_FILE.read_text(encoding="utf-8"))
    else:
        songs = []
        for filename in CATEGORY_FILE.values():
            text = (KB_DIR / filename).read_text(encoding="utf-8")
            for block in text.split("\n---"):
                title = re.findall(r"^## (.+)$", block, re.M)
                artist = re.search(r"^\*\*艺术家\*\*: (.+)$", block, re.M)
                if not title or not artist:
                    continue
                tags = {d.lower(): t.split(", ") for d, t in
                        re.findall(r"^\*\*(BASIC|ADVANCED|EXPERT|MASTER|REMASTER)\*\*: (.+)$", block, re.M)}
                aliases = re.search(r"^\*\*别名\*\*: (.+)$", block, re.M)
                songs.append({"title": title[-1], "artist": artist[1], "chart_tags": tags,
                              "aliases": re.sub(r" \(共\d+个\)$", "", aliases[1]).split(", ") if aliases else []})
    return {identity(s["title"], s["artist"]): s for s in songs}

CN_MAIDATA_URL = (
    "https://raw.githubusercontent.com/CrazyKidCN/"
    "maimaiDX-CN-songs-database/main/maidata.json"
)
DIVING_FISH_MUSIC_URL = "https://www.diving-fish.com/api/maimaidxprober/music_data"
ALIAS_URL = "https://www.yuzuchan.moe/api/maimaidx/maimaidxalias"
DETAIL_FALLBACK_URL = (
    "https://raw.githubusercontent.com/Choimoe/dxdataViewer/"
    "main/data/csv/merged/sheets.csv"
)

DIFFICULTIES = ["basic", "advanced", "expert", "master", "remaster"]
DIFF_LABEL = {
    "basic": "Basic",
    "advanced": "Advanced",
    "expert": "Expert",
    "master": "Master",
    "remaster": "Re:Master",
}
CN_KEYS = {
    "std": ["lev_bas", "lev_adv", "lev_exp", "lev_mas", "lev_remas"],
    "dx": ["dx_lev_bas", "dx_lev_adv", "dx_lev_exp", "dx_lev_mas", "dx_lev_remas"],
}
TYPE_OUT = {"std": "standard", "dx": "dx"}

CATEGORY_FILE = {
    "流行&动漫": "流行and动漫.md",
    "niconico＆VOCALOID™": "niconicoandVOCALOID.md",
    "舞萌": "舞萌.md",
    "东方Project": "东方Project.md",
    "其他游戏": "其他游戏.md",
    "音击/中二节奏": "音击-中二节奏.md",
}
VERSION_ORDER = [
    "maimai", "maimai PLUS", "GreeN", "GreeN PLUS", "ORANGE", "ORANGE PLUS",
    "PiNK", "PiNK PLUS", "MURASAKi", "MURASAKi PLUS", "MiLK", "MiLK PLUS",
    "FiNALE", "舞萌DX", "舞萌DX 2021", "舞萌DX 2022", "舞萌DX 2023",
    "舞萌DX 2024", "舞萌DX 2025", "舞萌DX 2026",
]


def fetch_json(url: str, timeout: int) -> Any:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_text(url: str, timeout: int) -> str:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.text


def norm(value: str) -> str:
    return re.sub(r"[\s（）()・･·]", "", (value or "").lower())


def artist_matches(left: str, right: str) -> bool:
    if norm(left) == norm(right):
        return True
    # 仅接受括号说明的增减，不把偶然包含的短艺术家名当作同一人。
    left, right = (re.sub(r"\s", "", s.lower()).replace("（", "(") for s in (left, right))
    return bool(left and right) and any(right.startswith(left + suffix) or left.startswith(right + suffix)
                                        for suffix in ("(", "feat.", "feat．"))


def title_norm(value: str) -> str:
    value = norm(value).replace(".", "").replace("．", "")
    return value.replace("bandver", "")


def ds_label(value: Any) -> Optional[str]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or not 1 <= number <= 15:
        return None
    integer = int(number)
    tenth = round((number - integer) * 10)
    return f"{integer}+" if tenth >= 7 else str(integer)


def load_old_rows() -> List[Dict[str, Any]]:
    if not LEVEL_INDEX.exists():
        return []
    data = json.loads(LEVEL_INDEX.read_text(encoding="utf-8"))
    return [row for rows in data.values() for row in rows]


def detail_rows_from_divingfish(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for song in data:
        if song.get("type") not in ("SD", "DX"):
            continue
        typ = "std" if str(song.get("type", "")).upper() == "SD" else "dx"
        levels = song.get("level") or []
        ds_values = song.get("ds") or []
        charts = song.get("charts") or []
        info = song.get("basic_info") or {}
        for i, level in enumerate(levels[:5]):
            chart = charts[i] if i < len(charts) else {}
            notes = chart.get("notes") or []
            names = ["tap", "hold", "slide", "touch", "break"] if typ == "dx" else ["tap", "hold", "slide", "break"]
            note_dict = {
                name: int(notes[j]) if j < len(notes) and notes[j] is not None else 0
                for j, name in enumerate(names)
            }
            rows.append({
                "source": "divingfish",
                "songId": str(song.get("id", "")),
                "songTitle": song.get("title", ""),
                "artist": info.get("artist", ""),
                "sheetType": typ,
                "difficulty": DIFFICULTIES[i],
                "level": str(level),
                "internalLevelValue": ds_values[i] if i < len(ds_values) else None,
                "noteDesigner": chart.get("charter"),
                "notes": note_dict,
            })
    return rows


def detail_rows_from_csv(text: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for row in csv.DictReader(io.StringIO(text)):
        typ = row.get("sheetType", "")
        if typ not in ("std", "dx"):
            continue
        notes = {
            "tap": int(row.get("noteTap") or 0),
            "hold": int(row.get("noteHold") or 0),
            "slide": int(row.get("noteSlide") or 0),
        }
        if typ == "dx":
            notes["touch"] = int(row.get("noteTouch") or 0)
        notes["break"] = int(row.get("noteBreak") or 0)
        rows.append({
            "source": "fallback",
            "songId": row.get("songId", ""),
            "songTitle": row.get("songTitle", ""),
            "artist": row.get("artist", ""),
            "sheetType": typ,
            "difficulty": row.get("difficulty", ""),
            "level": row.get("level", ""),
            "internalLevelValue": row.get("internalLevelValue") or None,
            "noteDesigner": row.get("noteDesigner") or None,
            "notes": notes,
        })
    return rows


def build_alias_map(payload: Any) -> Dict[str, List[str]]:
    if isinstance(payload, dict) and payload.get("code") == 0:
        payload = payload.get("content", [])
    result: Dict[str, List[str]] = {}
    if not isinstance(payload, list):
        return result
    for item in payload:
        sid = str(item.get("SongID", ""))
        aliases = item.get("Alias") or []
        if sid and isinstance(aliases, list):
            result[sid] = [str(x) for x in aliases if x]
    return result


def choose_group(
    song: Dict[str, Any],
    typ: str,
    by_title: Dict[str, List[Dict[str, Any]]],
    all_detail_rows: List[Dict[str, Any]],
) -> Optional[Tuple[str, List[Dict[str, Any]]]]:
    candidates = [r for r in by_title.get(song["title"], []) if r["sheetType"] == typ]
    if not candidates:
        candidates = [r for r in by_title.get(title_norm(song["title"]), []) if r["sheetType"] == typ]
    if not candidates and song["title"] == "Help me, ERINNNNNN!!" and typ == "std":
        candidates = [
            r for r in all_detail_rows
            if r.get("songTitle") == "Help me, ERINNNNNN!!（Band ver.）" and r["sheetType"] == "std"
        ]
    if not candidates:
        return None

    # 同名曲必须核对艺术家；Link(CoF) 在国服中也显示为 Link。
    artist = norm(song.get("artist", ""))
    exact = [r for r in candidates if norm(r.get("artist", "")) == artist]
    candidates = exact or [r for r in candidates if artist_matches(song.get("artist", ""), r.get("artist", ""))]
    if not candidates:
        return None

    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        groups[str(row["songId"])].append(row)

    scored = []
    for sid, rows in groups.items():
        score = 0
        left, right = norm(song.get("artist", "")), norm(rows[0].get("artist", ""))
        if left == right:
            score += 100
        elif left and right and (left in right or right in left):
            score += 60
        for i, diff in enumerate(DIFFICULTIES):
            current = song.get(CN_KEYS[typ][i]) or ""
            detail = next((r for r in rows if r["difficulty"] == diff), None)
            if current and detail and current == detail.get("level"):
                score += 10
            elif not current and detail is None:
                score += 1
        scored.append((score, sid, rows))

    scored.sort(reverse=True, key=lambda item: item[0])
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None
    _, sid, rows = scored[0]
    return sid, rows


def render_song(song: Dict[str, Any]) -> str:
    lines = [f"## {song['title']}", ""]
    lines.append(f"**ID**: {song.get('id') if song.get('id') is not None else '未知'}")
    if song.get("std_id") and song.get("dx_id") and song["std_id"] != song["dx_id"]:
        lines.append(f"**DX ID**: {song['dx_id']}")
    lines.extend([
        f"**艺术家**: {song['artist']}",
        f"**分类**: {song['category']}",
        f"**版本**: {song['version']}",
        "",
    ])

    aliases = song.get("aliases") or []
    if aliases:
        shown = ", ".join(aliases[:12])
        if len(aliases) > 12:
            shown += f" (共{len(aliases)}个)"
        lines.extend([f"**别名**: {shown}", ""])

    lines.extend(["### 难度信息", ""])
    for typ, label in (("standard", "标准谱面"), ("dx", "DX谱面")):
        data = song["difficulty"][typ]
        if any(data.values()):
            lines.append(f"**{label}**:")
            for diff in DIFFICULTIES:
                lines.append(f"- {DIFF_LABEL[diff]}: {data.get(diff) or '无'}")
            lines.append("")

    chart_tags = song.get("chart_tags") or {}
    if chart_tags:
        lines.extend(["### 谱面特征", ""])
        for diff in DIFFICULTIES:
            tags = chart_tags.get(diff) or []
            if tags:
                lines.append(f"**{diff.upper()}**: {', '.join(tags)}")
        lines.append("")

    tags = song.get("tags") or []
    if tags:
        lines.extend([f"**标签**: {', '.join(tags)}", ""])
    lines.extend(["---", ""])
    return "\n".join(line.rstrip() for line in lines)


def build_snapshot(timeout: int, cn_file: Optional[Path] = None,
                   details_file: Optional[Path] = None, aliases_file: Optional[Path] = None,
                   fallback_file: Optional[Path] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    cn = json.loads(cn_file.read_text(encoding="utf-8")) if cn_file else fetch_json(CN_MAIDATA_URL, timeout)
    if not isinstance(cn, list) or not cn:
        raise ValueError("国服曲库为空或格式错误，拒绝写入")
    old_rows = load_old_rows()
    annotations = load_annotations()
    title_counts = Counter(song["title"] for song in cn)

    old_exact: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    old_loose: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
    for row in old_rows:
        old_exact[(*identity(row.get("title", ""), row.get("artist", "")), row.get("type"), row.get("difficulty"))] = row
        old_loose[(row.get("title"), row.get("type"), row.get("difficulty"))] = row

    def old_for(song: Dict[str, Any], typ: str, diff: str) -> Optional[Dict[str, Any]]:
        row = old_exact.get((*identity(song["title"], song.get("artist", "")), TYPE_OUT[typ], diff))
        if row is None and title_counts[song["title"]] == 1:
            candidate = old_loose.get((song["title"], TYPE_OUT[typ], diff))
            if candidate and artist_matches(song.get("artist", ""), candidate.get("artist", "")):
                row = candidate
        return row

    try:
        payload = json.loads(details_file.read_text(encoding="utf-8")) if details_file and details_file.suffix == ".json" else None
        detail_rows = (detail_rows_from_csv(details_file.read_text(encoding="utf-8")) if details_file and details_file.suffix == ".csv"
                       else detail_rows_from_divingfish(payload if payload is not None else fetch_json(DIVING_FISH_MUSIC_URL, timeout)))
        if not detail_rows:
            raise ValueError("谱面详情为空")
        print(f"[detail] Diving-Fish: {len(detail_rows)} chart rows")
    except Exception as exc:
        print(f"[detail] Diving-Fish unavailable, fallback to dxdataViewer: {exc}")
        detail_rows = detail_rows_from_csv(fallback_file.read_text(encoding="utf-8") if fallback_file
                                          else fetch_text(DETAIL_FALLBACK_URL, timeout))
        if not detail_rows:
            raise ValueError("主源与备用谱面详情均不可用，拒绝写入")

    by_title: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in detail_rows:
        by_title[row["songTitle"]].append(row)
        by_title[title_norm(row["songTitle"])].append(row)
        if row["songTitle"] in TITLE_EQUIVALENTS:
            by_title[TITLE_EQUIVALENTS[row["songTitle"]]].append(row)

    # 水鱼可能缺少仍在国服的曲目；只用备用源补齐安全匹配的缺失组。
    fallback_rows = []
    fallback_by_title: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    if any(any(song.get(k) for k in CN_KEYS[typ]) and choose_group(song, typ, by_title, detail_rows) is None
           for song in cn for typ in ("std", "dx")):
        try:
            fallback_rows = detail_rows_from_csv(fallback_file.read_text(encoding="utf-8") if fallback_file
                                                else fetch_text(DETAIL_FALLBACK_URL, timeout))
            for row in fallback_rows:
                fallback_by_title[row["songTitle"]].append(row)
                fallback_by_title[title_norm(row["songTitle"])].append(row)
                if row["songTitle"] in TITLE_EQUIVALENTS:
                    fallback_by_title[TITLE_EQUIVALENTS[row["songTitle"]]].append(row)
            print(f"[detail] 备用源补缺: {len(fallback_rows)} chart rows")
        except Exception as exc:
            print(f"[detail] 备用源不可用，未匹配详情保留 null: {exc}")

    try:
        alias_map = build_alias_map(json.loads(aliases_file.read_text(encoding="utf-8")) if aliases_file else fetch_json(ALIAS_URL, timeout))
        if not alias_map:
            raise ValueError("别名响应为空或格式错误")
        print(f"[alias] live entries: {len(alias_map)}")
    except Exception as exc:
        print(f"[alias] live API unavailable, keep local aliases: {exc}")
        alias_map = {}

    songs: List[Dict[str, Any]] = []
    level_rows: List[Dict[str, Any]] = []

    for song in cn:
        annotation = annotations.get(identity(song["title"], song.get("artist", "")), {})
        if not annotation:
            matches = [s for (title, artist), s in annotations.items()
                       if title == title_norm(song["title"]) and artist_matches(song.get("artist", ""), s.get("artist", ""))]
            if len(matches) == 1:
                annotation = matches[0]
        chosen = {
            typ: (choose_group(song, typ, by_title, detail_rows)
                  or choose_group(song, typ, fallback_by_title, fallback_rows))
                  if any(song.get(k) for k in CN_KEYS[typ]) else None
            for typ in ("std", "dx")
        }
        ids = {typ: (chosen[typ][0] if chosen[typ] else None) for typ in ("std", "dx")}
        for typ in ("std", "dx"):
            if ids[typ] is None:
                old_ids = {str(r["id"]) for diff in DIFFICULTIES
                           if song.get(CN_KEYS[typ][DIFFICULTIES.index(diff)])
                           for r in [old_for(song, typ, diff)] if r and r.get("id") is not None}
                if len(old_ids) == 1:
                    ids[typ] = next(iter(old_ids))

        aliases = [song["title"]]
        aliases.extend(annotation.get("aliases") or [])
        for sid in (ids["std"], ids["dx"]):
            aliases.extend(alias_map.get(str(sid), []))
        for row in old_rows:
            if row.get("title") == song["title"] and (
                norm(row.get("artist", "")) == norm(song.get("artist", ""))
                or (title_counts[song["title"]] == 1 and artist_matches(song.get("artist", ""), row.get("artist", "")))
            ):
                aliases.extend(row.get("aliases") or [])
                break
        aliases = list(dict.fromkeys(re.sub(r"[\r\n]+", " ", alias).strip() for alias in aliases if alias.strip()))

        difficulty = {"standard": {}, "dx": {}}
        tags_by_diff: Dict[str, List[str]] = {d: list(t) for d, t in (annotation.get("chart_tags") or {}).items()}

        for typ in ("std", "dx"):
            group_rows = chosen[typ][1] if chosen[typ] else []
            for i, diff in enumerate(DIFFICULTIES):
                value = song.get(CN_KEYS[typ][i]) or None
                difficulty[TYPE_OUT[typ]][diff] = value
                if not value:
                    continue

                detail = next((r for r in group_rows if r["difficulty"] == diff), None)
                old = old_for(song, typ, diff)

                ds = None
                ds_source = None
                if detail and detail.get("internalLevelValue") is not None:
                    candidate = detail["internalLevelValue"]
                    if ds_label(candidate) == value:
                        ds = float(candidate)
                        ds_source = detail["source"]
                # 最新源冲突时不回填旧定数，以免把过时值当作国服精确定数。
                if detail is None and old and old.get("ds") is not None and ds_label(old["ds"]) == value:
                    ds = float(old["ds"])
                    ds_source = "local"

                chart_tags = list(dict.fromkeys((old or {}).get("chart_tags") or []))
                if chart_tags:
                    tags_by_diff[diff] = list(dict.fromkeys(tags_by_diff.get(diff, []) + chart_tags))

                notes = detail.get("notes") if detail else (old or {}).get("notes")
                charter = (detail or {}).get("noteDesigner") or (old or {}).get("charter")

                sid = ids[typ]
                if sid is None and old and old.get("id") is not None:
                    sid = str(old["id"])
                level_rows.append({
                    "id": int(sid) if sid and str(sid).isdigit() else sid,
                    "title": song["title"],
                    "aliases": aliases,
                    "artist": song.get("artist", ""),
                    "category": song.get("category", ""),
                    "version": song.get("version", ""),
                    "type": TYPE_OUT[typ],
                    "difficulty": diff,
                    "value": value,
                    "ds": ds,
                    "ds_source": ds_source,
                    "detail_source": detail["source"] if detail else "local" if old else None,
                    "charter": charter,
                    "notes": notes,
                    "chart_tags": chart_tags,
                })

        tags = {song.get("artist", ""), song.get("category", ""), song.get("version", "")}
        for sep in ("&", "＆", "/"):
            if sep in song.get("category", ""):
                tags.update(part.strip() for part in song["category"].split(sep) if part.strip())
        for values in tags_by_diff.values():
            tags.update(values)

        primary = ids["std"] or ids["dx"]
        songs.append({
            "id": int(primary) if primary and str(primary).isdigit() else primary,
            "std_id": int(ids["std"]) if ids["std"] and str(ids["std"]).isdigit() else ids["std"],
            "dx_id": int(ids["dx"]) if ids["dx"] and str(ids["dx"]).isdigit() else ids["dx"],
            "title": song["title"],
            "artist": song.get("artist", ""),
            "category": song.get("category", ""),
            "version": song.get("version", ""),
            "aliases": aliases,
            "image_file": song.get("image_file", ""),
            "difficulty": difficulty,
            "chart_tags": tags_by_diff,
            "tags": sorted(tag for tag in tags if tag),
        })

    return songs, level_rows


def validate_snapshot(songs: List[Dict[str, Any]], rows: List[Dict[str, Any]]) -> None:
    """写入前验证曲目唯一性、完整谱面集合、等级/定数、ID 和音符数据。"""
    keys = [identity(s["title"], s["artist"]) for s in songs]
    if len(keys) != len(set(keys)):
        raise ValueError("重复歌曲身份")
    expected = {(identity(s["title"], s["artist"]), typ, diff, value)
                for s in songs for typ, values in s["difficulty"].items()
                for diff, value in values.items() if value}
    actual = [(identity(r["title"], r["artist"]), r["type"], r["difficulty"], r["value"]) for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("重复、缺失或多余谱面")
    ids = {}
    songs_by_key = {identity(s["title"], s["artist"]): s for s in songs}
    for s in songs:
        if s["category"] not in CATEGORY_FILE:
            raise ValueError(f"未知分类: {s['category']}")
    for r in rows:
        expected_id = songs_by_key[identity(r["title"], r["artist"])]["std_id" if r["type"] == "standard" else "dx_id"]
        if r["id"] != expected_id:
            raise ValueError("歌曲与谱面ID不一致")
        if not re.fullmatch(r"(?:[1-9]|1[0-4])\+?|15", r["value"]):
            raise ValueError(f"无效显示等级: {r['value']}")
        if r["ds"] is not None and ds_label(r["ds"]) != r["value"]:
            raise ValueError("定数与显示等级不一致")
        if r["id"] is not None:
            owner = (identity(r["title"], r["artist"]), r["type"])
            if r["id"] in ids and ids[r["id"]] != owner:
                raise ValueError(f"ID误配: {r['id']}")
            ids[r["id"]] = owner
        if r["notes"] is not None and any(not isinstance(n, int) or n < 0 for n in r["notes"].values()):
            raise ValueError("音符数必须是非负整数")
        if not isinstance(r["aliases"], list) or not isinstance(r["chart_tags"], list):
            raise ValueError("别名/标签格式错误")


def write_snapshot(songs: List[Dict[str, Any]], level_rows: List[Dict[str, Any]]) -> None:
    validate_snapshot(songs, level_rows)
    SONGS_FILE.write_text(json.dumps(songs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    def level_key(value: str) -> Tuple[int, str]:
        match = re.match(r"^(\d+)(\+)?", value)
        if not match:
            return (999, value)
        return (int(match.group(1)) * 2 + (1 if match.group(2) else 0), value)

    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in level_rows:
        grouped[row["value"]].append(row)
    ordered: Dict[str, List[Dict[str, Any]]] = {}
    for key in sorted(grouped, key=level_key):
        ordered[key] = sorted(
            grouped[key],
            key=lambda row: (row["title"], row["type"], DIFFICULTIES.index(row["difficulty"])),
        )
    LEVEL_INDEX.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    KB_DIR.mkdir(exist_ok=True)
    version_rank = {version: i for i, version in enumerate(VERSION_ORDER)}
    for category, filename in CATEGORY_FILE.items():
        current = [song for song in songs if song["category"] == category]
        by_version: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for song in current:
            by_version[song["version"]].append(song)
        parts = [f"# {category}\n\n本分类共有 {len(current)} 条歌曲记录。\n"]
        for version in sorted(by_version, key=lambda v: (version_rank.get(v, 999), v)):
            items = by_version[version]
            parts.append(f"\n## {version} ({len(items)}首)\n")
            parts.extend("\n" + render_song(song) for song in items)
        (KB_DIR / filename).write_text("".join(parts), encoding="utf-8")

    version_count = Counter(song["version"] for song in songs)
    category_count = Counter(song["category"] for song in songs)
    tagged = sum(1 for song in songs if song["chart_tags"])
    associations = sum(
        sum(len(values) for values in song["chart_tags"].values())
        for song in songs
    )
    all_tags = sorted({
        tag
        for song in songs
        for values in song["chart_tags"].values()
        for tag in values
    })

    lines = [
        "# 舞萌DX歌曲知识库索引",
        "",
        f"共有 **{len(songs)} 条歌曲记录**（{len({song['title'] for song in songs})} 个唯一标题）。",
        f"共有 **{len(level_rows)} 张常规谱面**。",
        "",
        "曲目、分类、版本和显示等级以国服曲库为准；精确定数仅在能与当前国服显示等级可靠对应时保留。",
        "",
        "## 按版本分类",
        "",
    ]
    for version in sorted(version_count, key=lambda v: (version_rank.get(v, 999), v)):
        lines.append(f"- **{version}**: {version_count[version]} 首歌曲")
    lines.extend(["", "## 按分类分类", ""])
    for category, filename in CATEGORY_FILE.items():
        lines.append(f"- [{category}](./{filename}): {category_count[category]} 首歌曲")
    lines.extend([
        "", "## 别名统计", "",
        f"- 包含别名的歌曲: {sum(bool(s['aliases']) for s in songs)} 首",
        f"- 总别名数量（含标题）: {sum(len(s['aliases']) for s in songs)} 个",
    ])
    lines.extend([
        "", "## 谱面特征统计", "",
        f"- 包含谱面特征的歌曲: {tagged} 首",
        f"- 总标签关联数（每首歌曲各难度内去重）: {associations} 个",
        "", "## 可用的谱面特征标签", "",
    ])
    lines.extend(f"- {tag}" for tag in all_tags)
    lines.extend([
        "", "## 搜索提示", "",
        "可以按标题、别名、艺术家、分类、版本、显示等级和谱面特征进行组合查询。",
        "精确定数无法安全对齐时，level_index.json 中的 ds 为 null，不做猜测。",
        "",
    ])
    (KB_DIR / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cn-file", type=Path, help="使用本地国服源 JSON")
    parser.add_argument("--details-file", type=Path, help="使用本地水鱼 JSON 或备用 CSV")
    parser.add_argument("--fallback-file", type=Path, help="使用本地备用 CSV 补缺")
    parser.add_argument("--aliases-file", type=Path, help="使用本地别名 JSON；空列表表示保留现有别名")
    parser.add_argument("--validate-only", action="store_true", help="离线校验已提交快照")
    parser.add_argument("--render-only", action="store_true", help="离线重建 Markdown 和索引")
    args = parser.parse_args()

    if args.validate_only or args.render_only:
        songs = json.loads(SONGS_FILE.read_text(encoding="utf-8"))
        level_rows = load_old_rows()
    else:
        songs, level_rows = build_snapshot(args.timeout, args.cn_file, args.details_file, args.aliases_file, args.fallback_file)
    validate_snapshot(songs, level_rows)
    print(f"歌曲记录: {len(songs)}；谱面记录: {len(level_rows)}")
    if args.dry_run or args.validate_only:
        return
    write_snapshot(songs, level_rows)
    print("✅ level_index.json 与 knowledge_base/*.md 已更新")


if __name__ == "__main__":
    main()
