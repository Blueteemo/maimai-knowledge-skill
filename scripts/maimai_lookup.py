"""
maimai_lookup.py — 舞萌DX查分器集成脚本
基于 maimai-py 封装，支持通过QQ号或水鱼用户名查询玩家B50、Rating等信息。
使用方法: python maimai_lookup.py <developer_token> <qq|username> <value>

依赖: pip install maimai-py

示例:
    python maimai_lookup.py YOUR_TOKEN qq 114514
    python maimai_lookup.py YOUR_TOKEN username example_user
"""

import asyncio
import sys
import json


async def lookup_player(developer_token: str, identifier_type: str, identifier_value: str):
    """查询玩家B50信息"""
    from maimai_py import MaimaiClient, PlayerIdentifier, DivingFishProvider

    maimai = MaimaiClient()
    divingfish = DivingFishProvider(developer_token=developer_token)

    # 构造查询标识
    if identifier_type == "qq":
        identifier = PlayerIdentifier(qq=int(identifier_value))
    elif identifier_type == "username":
        identifier = PlayerIdentifier(username=identifier_value)
    else:
        raise ValueError("identifier_type 必须是 qq 或 username")

    # 并行查询玩家信息和分数
    player_task = maimai.players(identifier, provider=divingfish)
    scores_task = maimai.scores(identifier, provider=divingfish)
    
    player, scores = await asyncio.gather(player_task, scores_task)

    b35 = scores.scores_b35
    b15 = scores.scores_b15

    result = {
        "name": player.name,
        "nickname": player.nickname,
        "rating": player.rating,
        "additional_rating": player.additional_rating,
        "plate": player.plate,
        "b35_rating": scores.rating_b35,
        "b15_rating": scores.rating_b15,
        "b35": [
            {
                "title": s.title,
                "level": s.level,
                "level_value": s.level_value,
                "achievements": s.achievements,
                "dx_rating": s.dx_rating,
                "fc": str(s.fc) if s.fc else None,
                "fs": str(s.fs) if s.fs else None,
                "type": str(s.type),
                "level_index": str(s.level_index),
                "play_count": s.play_count,
            }
            for s in b35
        ],
        "b15": [
            {
                "title": s.title,
                "level": s.level,
                "level_value": s.level_value,
                "achievements": s.achievements,
                "dx_rating": s.dx_rating,
                "fc": str(s.fc) if s.fc else None,
                "fs": str(s.fs) if s.fs else None,
                "type": str(s.type),
                "level_index": str(s.level_index),
                "play_count": s.play_count,
            }
            for s in b15
        ],
    }

    return result


def format_player_text(data: dict) -> str:
    """将查询结果格式化为可读文本"""
    lines = []
    lines.append(f"🎵 **{data['nickname']}**（{data['name']}）")
    lines.append(f"⭐ 总 Rating: **{data['rating']}** (B35: {data['b35_rating']} + B15: {data['b15_rating']})")
    if data.get("plate"):
        lines.append(f"🏅 当前姓名框: {data['plate']}")
    lines.append("")

    lines.append("**B35 (旧曲) TOP5:**")
    for i, s in enumerate(data["b35"][:5], 1):
        lv = s["level_value"] or s["level"]
        fc_str = f" AP" if s["fc"] == "FCType.AP" else (f" FC" if s["fc"] in ("FCType.FC", "FCType.FCP") else "")
        fs_str = f" Sync" if s["fs"] == "FSType.SYNC" else ""
        lines.append(f"  {i}. {s['title']} [Lv.{lv}] - {s['achievements']}% - {s['dx_rating']}DX{fc_str}{fs_str}")
    lines.append("")

    lines.append("**B15 (新曲) TOP5:**")
    for i, s in enumerate(data["b15"][:5], 1):
        lv = s["level_value"] or s["level"]
        fc_str = f" AP" if s["fc"] == "FCType.AP" else (f" FC" if s["fc"] in ("FCType.FC", "FCType.FCP") else "")
        fs_str = f" Sync" if s["fs"] == "FSType.SYNC" else ""
        lines.append(f"  {i}. {s['title']} [Lv.{lv}] - {s['achievements']}% - {s['dx_rating']}DX{fc_str}{fs_str}")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python maimai_lookup.py <token> <qq|username> <value>")
        print("示例:")
        print("  python maimai_lookup.py TOKEN qq 114514")
        print("  python maimai_lookup.py TOKEN username example_user")
        sys.exit(1)

    token = sys.argv[1]
    id_type = sys.argv[2]
    id_value = sys.argv[3]

    result = asyncio.run(lookup_player(token, id_type, id_value))
    print(format_player_text(result))
