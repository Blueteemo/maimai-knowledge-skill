# 🎵 舞萌DX歌曲知识库

查询国服歌曲、别名、显示等级、定数和谱面特征，并通过现有工具查 B50、封面和拟合难度。

当前全量快照：**CN1.56-E**（国服源更新于 2026-10-01），**1293 条歌曲记录、1292 个唯一标题、5516 张常规谱面、6 个分类**。两首 `Link` 按艺术家区分，不能只按标题去重。

## 文件结构

| 文件 | 用途 |
| --- | --- |
| `SKILL.md` | AstrBot / OpenCode 的查询与工具说明 |
| `songs.json` | 完整国服歌曲快照，含标准/DX ID、别名及保留标签 |
| `level_index.json` | 按精确显示等级分组的谱面索引，如 `12`、`12+` |
| `knowledge_base/INDEX.md` | 自动生成的分类、版本与标签统计 |
| `knowledge_base/*.md` | 六个分类的歌曲查询文档 |
| `scripts/update_knowledge_base.py` | 全量同步、详情补缺、校验与生成的统一入口 |
| `scripts/generate_kb.py` | 从已提交快照离线重建的兼容入口 |
| `scripts/maimai_lookup.py` | 现有 Developer-Token 查分工具 |
| `scripts/maimai_utils.py` | 封面与拟合难度工具 |

## 安装与查询

```bash
git clone https://github.com/Blueteemo/maimai-knowledge-skill.git
cd maimai-knowledge-skill
pip install requests maimai-py
```

将仓库放到 AstrBot 的 skills 目录并重新加载；OpenCode 可按其技能目录配置使用。静态歌曲查询不需要 Token，也不需要访问网络。

```bash
python scripts/maimai_lookup.py YOUR_TOKEN qq 114514
python scripts/maimai_lookup.py YOUR_TOKEN username example_user
python scripts/maimai_utils.py --help
```

**Developer-Token 将于 2027-01-01 00:00（UTC+8）失效。** 本次保留查分逻辑，只注明失效时间；OAuth 迁移后续另行处理。

## 数据与优先级

1. [国服曲库](https://github.com/CrazyKidCN/maimaiDX-CN-songs-database)：决定收录范围、标题、艺术家、分类、版本和显示等级。同步目标为常规 SD/DX 谱面，不收录宴谱。
2. [水鱼 music_data](https://www.diving-fish.com/api/maimaidxprober/music_data)：补充谱面 ID、精确定数、谱师与音符数，无需 Developer-Token。
3. [备用谱面 CSV](https://github.com/Choimoe/dxdataViewer/blob/main/data/csv/merged/sheets.csv)：水鱼不可用或缺少曲目时补缺，仍受国服曲库范围与等级约束。
4. [别名 API](https://www.yuzuchan.moe/api/maimaidx/maimaidxalias)：合并在线和已有别名；失败时保留已有别名。

本快照全部 5516 张谱面已匹配 ID；5437 张使用水鱼详情、79 张使用备用详情。2139 张谱面的 `ds` 为 `null`，表示没有能与国服显示等级安全对应的定数。`ds_source` 和 `detail_source` 记录来源；不可把空定数解释为 0，也不可用其他版本的显示等级覆盖国服。

保留原有 926 首含标签歌曲。旧 Markdown 标签未区分 SD/DX，因此 `songs.json.chart_tags` 为歌曲层的历史参考；谱面查询应优先使用 `level_index.json.chart_tags`。新曲不凭空生成配置标签，历史标签不保证仍适合新谱面。

## 更新与校验

从任意工作目录调用统一入口（路径以脚本所在仓库为准）：

```bash
python scripts/update_knowledge_base.py --dry-run
python scripts/update_knowledge_base.py
python scripts/update_knowledge_base.py --validate-only
python scripts/update_knowledge_base.py --render-only
python -m unittest discover -s tests
git diff --check
```

首次命令抓取并验证，但不写文件。正式同步先完成抓取、匹配与校验，再更新歌曲快照、等级索引和 Markdown。校验空源、重复身份、谱面完整性、等级/定数一致性、ID 误配和音符数；失败时退出，不发布未经校验的结果。

支持本地源复现，避免测试依赖实时接口：

```bash
python scripts/update_knowledge_base.py --cn-file /path/maidata.json \
  --details-file /path/music_data.json --fallback-file /path/sheets.csv \
  --aliases-file /path/aliases.json --dry-run
```

`--details-file` 也支持备用 CSV。别名文件为 `[]` 时保留本地别名。离线重建不更新网络源；新增全量同步时应同时核对国服源 README 的版本，更新本文的快照标识和统计。

旧 `match_ids.py`、`convert_maidata.py`、`integrate_alias.py`、`integrate_tags.py` 保留为历史工具，不再作为更新流水线；它们依赖仓库未附带的旧中间文件。`generate_kb.py` 已接入新快照。

## 许可证

本仓库仅供学习和个人使用。上游曲目数据、别名和社区标签保留各自来源与权利归属。
