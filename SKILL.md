---
name: maimai-knowledge
description: 舞萌DX歌曲知识库查询和分析。使用当用户询问舞萌歌曲信息、难度、分类、版本、艺术家、谱面特征、别名等。
---

# 舞萌DX歌曲知识库

这是一个专门用于查询和分析舞萌DX歌曲数据的skill，集成 [maimai-py](https://github.com/TrueRou/maimai.py) SDK 支持实时查分功能。

## 功能特性

### 1. 歌曲查询
- 按标题、艺术家、分类、版本查询歌曲
- 按难度等级查询歌曲
- 按标签查询歌曲
- 按谱面特征查询歌曲（转圈、扫键、散打等）
- 按别名查询歌曲（如"甩葱歌"、"千本樱"等）

### 2. 难度分析
- 查询歌曲的标准谱面和DX谱面难度
- 分析难度分布
- 比较不同歌曲的难度

### 3. 谱面特征分析
- 查询歌曲的谱面特征标签
- 按特征筛选歌曲（如"有转圈的歌曲"）
- 分析不同难度的谱面特征

### 4. 统计信息
- 按分类统计歌曲数量
- 按版本统计歌曲数量
- 难度分布统计
- 谱面特征统计

### 5. 玩家查分（基于 maimai-py）
- 通过 QQ 号或水鱼用户名查询玩家信息（Rating、昵称、姓名框）
- 查询玩家 B50 成绩（B35旧曲 + B15新曲），含谱面定数、达成率、DX评分、FC/FS状态
- 数据源：水鱼查分器（DivingFish），需提供 developer_token

### 6. 扩展工具（基于 maimai_utils.py）
- **歌曲封面获取**：通过歌曲ID获取水鱼封面图（`/covers/{id}.png`），支持原始数字ID自动处理（旧歌补0至5位，10001~11000区间自动减10000）
- **拟合难度查询**：通过 `/chart_stats` 端点获取谱面拟合难度数据（比官标定数更精确的拟合定数、平均达成率、样本量）
- **命令行工具**：`scripts/maimai_utils.py` 支持 `cover`、`fitdiff`、`stats` 三个子命令

## 数据结构

每首歌曲包含以下信息：
- `id`: 官方歌曲ID
- `title`: 歌曲标题
- `artist`: 艺术家
- `category`: 分类（流行&动漫、niconico＆VOCALOID™、舞萌、东方Project、其他游戏、音击/中二节奏）
- `version`: 版本（maimai、maimai PLUS、GreeN、GreeN PLUS、PiNK、PiNK PLUS、MURASAKi、MURASAKi PLUS、MiLK、MiLK PLUS、FiNALE、舞萌DX等）
- `difficulty`: 难度信息
  - `standard`: 标准谱面（basic、advanced、expert、master、remaster）
  - `dx`: DX谱面（同上）
  - `utage`: 宴谱（如有）
- `aliases`: 歌曲别名/外号列表（如"甩葱歌"、"千本樱"等）
- `chart_tags`: 谱面特征标签（按难度分类）
  - `basic`: Basic难度的特征标签
  - `advanced`: Advanced难度的特征标签
  - `expert`: Expert难度的特征标签
  - `master`: Master难度的特征标签
  - `remaster`: Re:Master难度的特征标签
- `tags`: 所有标签（包括谱面特征标签）

### 谱面特征标签说明

谱面特征标签描述了歌曲谱面的特殊配置和玩法：

**操作类标签**：
- **转圈**: 需要完成大于等于8个键的顺时针或逆时针转圈
- **扫键**: 需要快速扫过2个或以上键
- **散打**: 需要完成具有较大范围的位移的高密度Tap
- **交互**: 交替击打两个键
- **反手**: 需要将手臂交叉才可以完成的配置
- **一笔画**: 由多个星星组成，需要连续完成星星条

**难度类标签**：
- **底力谱**: 底力特训谱
- **体力谱**: 体力特训谱
- **高物量**: 音符数量特别多
- **爆发**: 需要短时间内完成大量操作
- **纵连**: 需要连续快速击打同一个键
- **跳拍**: 需要跳过节拍的配置
- **拆弹**: 需要精确控制的配置

**评价类标签**：
- **水**: 难度较低，容易完成
- **绝赞段**: 包含绝赞段落（可能影响分数）

## 集成说明

本 skill 集成了 [maimai-py](https://github.com/TrueRou/maimai.py)（v1.4.2+）用于实时查分。

### 安装依赖

```bash
pip install maimai-py
```

### 数据源配置

使用水鱼查分器（DivingFish）作为数据源，需要提供 `developer_token`：

```python
from maimai_py import MaimaiClient, PlayerIdentifier, DivingFishProvider

maimai = MaimaiClient()
divingfish = DivingFishProvider(developer_token="your_token_here")
```

### 查询方式

支持两种玩家标识查询：

1. **通过 QQ 号**（推荐，群聊场景最便捷）
   ```python
   identifier = PlayerIdentifier(qq=114514)
   ```

2. **通过水鱼用户名**
   ```python
   identifier = PlayerIdentifier(username="example_user")
   ```

### 查询玩家信息

```python
# 获取玩家概要信息
player = await maimai.players(identifier, provider=divingfish)
# player.nickname, player.rating, player.plate, ...

# 获取 B50 成绩
scores = await maimai.scores(identifier, provider=divingfish)
# scores.rating, scores.rating_b35, scores.rating_b15
# scores.scores_b35 (B35列表), scores.scores_b15 (B15列表)

# 每条记录包含: title, level, level_value, achievements,
#                dx_rating, fc, fs, play_count, type, level_index
```

### 快速查询脚本

`scripts/maimai_lookup.py` 提供了命令行查询工具：

```bash
# 通过QQ号查询
python scripts/maimai_lookup.py YOUR_TOKEN qq 114514

# 通过用户名查询
python scripts/maimai_lookup.py YOUR_TOKEN username example_user
```

## 使用示例

### 玩家查分（基于 maimai-py）
用户：查一下我的B50
助手：根据发送者的QQ号查询水鱼查分器，返回B50成绩（Rating、B35及B15 TOP5）

用户：查一下某位玩家的B50
助手：根据提供的QQ号或水鱼用户名查询，返回对应玩家的B50成绩

用户：查询某人的Rating
助手：查询对应玩家的Rating信息，返回总Rating、B35及B15分数

### 按难度查询
用户：有哪些Master难度13+的歌曲？
助手：筛选Master难度为13+的歌曲列表

### 按分类查询
用户：东方Project有多少首歌？
助手：统计东方Project分类的歌曲数量

### 按版本查询
用户：舞萌DX版本有哪些新歌？
助手：筛选版本为"舞萌DX"的歌曲

### 难度比较
用户：比较一下《カゲロウデイズ》和《ロストワンの号哭》的难度
助手：返回两首歌曲的难度对比

### 按谱面特征查询
用户：有哪些有转圈的歌曲？
助手：筛选包含"转圈"标签的歌曲列表

用户：Master难度有哪些散打谱？
助手：筛选Master难度包含"散打"标签的歌曲

用户：找一下有交互和反手配置的歌曲
助手：筛选同时包含"交互"和"反手"标签的歌曲

### 查询歌曲的谱面特征
用户：《カゲロウデイズ》有什么谱面特征？
助手：返回该歌曲各难度的谱面特征标签

### 歌曲封面获取
用户：给我看看伊吕波歌的封面
助手：根据歌曲ID获取封面图，ID自动补0至5位，返回图片

### 拟合难度查询
用户：查一下《トーキョーゲットー》的拟合定数
助手：获取该歌曲所有谱面的拟合难度数据（拟合定数、平均达成率、样本量）

### 按别名查询
用户：甩葱歌是哪首？
助手：搜索别名包含"甩葱歌"的歌曲，返回《Ievan Polkka》

用户：千本樱的Master难度是多少？
助手：搜索别名包含"千本樱"的歌曲，返回《千本桜》的Master难度信息

用户：帮我查一下砂の惑星
助手：搜索别名或标题包含"砂の惑星"的歌曲，返回《砂の惑星 feat. HATSUNE MIKU》

## 查询方法

### 1. 使用知识库文件（Markdown）
知识库文件位于 `knowledge_base/` 目录下：
- `INDEX.md`: 总索引文件
- `流行and动漫.md`: 流行&动漫分类
- `niconicoandVOCALOID.md`: niconico＆VOCALOID™分类
- `舞萌.md`: 舞萌分类
- `东方Project.md`: 东方Project分类
- `其他游戏.md`: 其他游戏分类
- `音击-中二节奏.md`: 音击/中二节奏分类

### 3. 使用 maimai-py SDK 进行实时查分

本 skill 集成了 maimai-py，支持通过 QQ 号或水鱼用户名查询玩家实时数据。使用方式见上方「集成说明」章节。

**典型场景**：
- 用户直接问"查B50"、"查Rating" → 使用水鱼查分器，通过发送者QQ号查询
- 用户问"查XXX的B50" → 通过被提及用户的QQ号查询
- 需要歌曲定数、达成率、FC/FS等详细信息

**注意**：需要配置 DivingFish provider 的 developer_token，且目标用户需在对应查分器平台绑定过数据。

### 2. 使用JSON索引文件（推荐，查询效率最高）

**`level_index.json`**: 按难度分组的快速索引文件。
- 结构：`{"12": [{"title": "...", "aliases": [...], "artist": "...", "category": "...", "version": "...", "type": "standard|dx", "difficulty": "master|expert|...", "value": "12+", "chart_tags": ["交互", "扫键", ...]}, ...], "13": [...]}`
- 查询示例：要查难度12的歌，直接读取 `data['12']` 即可，无需解析Markdown
- 支持按难度+谱面特征联合筛选：如 `[s for s in data['12'] if '水' in s['chart_tags']]`
- 支持按别名搜索：`[s for s in data['12'] if '陕北民歌' in s['aliases']]`

## 查询技巧

1. **模糊匹配**：标题、艺术家和别名支持模糊匹配
2. **多条件筛选**：可以同时按多个条件筛选
3. **标签搜索**：使用标签可以快速找到相关歌曲
4. **难度范围**：可以查询特定难度范围的歌曲
5. **谱面特征搜索**：可以按谱面特征标签搜索歌曲
6. **别名搜索**：使用歌曲的别名/外号搜索（如"甩葱歌"、"千本樱"）
7. **组合查询**：可以组合多个条件，如"有转圈的Master难度13+歌曲"

## 注意事项

1. 数据来源于 diving-fish API，可能与游戏内数据略有差异
2. 部分歌曲可能缺少某些难度谱面
3. 标签是自动生成的，可能不完全准确
4. 宴谱（utage）数据可能不完整

## 更新数据

如需更新数据，可以：
1. 运行 `match_ids.py` 更新官方ID映射
2. 运行 `convert_maidata.py` 重新生成JSON数据
3. 运行 `generate_kb.py` 重新生成知识库文件