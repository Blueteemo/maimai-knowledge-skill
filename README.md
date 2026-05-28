# 舞萌DX歌曲知识库 Skill 包

这是一个AstrBot skill包，包含舞萌DX歌曲知识库，支持按谱面特征查询和实时查分（基于 maimai-py）。

## 安装方法

### 方法1：直接安装（推荐）
1. 将 `maimai-knowledge-skill.zip` 解压到opencode的skills目录：
   - 全局安装：`~/.config/opencode/skills/`
   - 项目安装：`.opencode/skills/`

2. 重启opencode

### 方法2：手动安装
1. 解压zip文件
2. 将 `maimai-knowledge` 文件夹复制到skills目录
3. 将 `knowledge_base` 文件夹放在合适的位置
4. 在 `SKILL.md` 中更新 `knowledge_base` 的路径

## 文件结构

```
maimai-knowledge-skill.zip
├── SKILL.md                    # skill定义文件
├── README.md                   # 本文件
├── knowledge_base/             # 知识库文件
│   ├── INDEX.md                # 总索引
│   ├── 流行and动漫.md          # 流行&动漫分类
│   ├── niconicoandVOCALOID.md  # niconico＆VOCALOID™分类
│   ├── 舞萌.md                 # 舞萌分类
│   ├── 东方Project.md          # 东方Project分类
│   ├── 其他游戏.md             # 其他游戏分类
│   └── 音击-中二节奏.md        # 音击/中二节奏分类
└── scripts/                    # 数据更新脚本
    ├── match_ids.py            # 官方ID匹配脚本
    ├── convert_maidata.py      # 数据转换脚本
    ├── integrate_tags.py       # 标签整合脚本
    └── generate_kb.py          # 知识库生成脚本
```

## 功能特性

### 0. 玩家查分（基于 maimai-py）
- 通过 QQ 号或水鱼用户名查询玩家 B50 成绩
- 支持查 Rating、B35/B15 分数、谱面达成率、DX评分、FC/FS状态
- 数据源：水鱼查分器（DivingFish），需配置 developer_token
- 依赖安装：`pip install maimai-py`
- 快速查询脚本：`scripts/maimai_lookup.py`

### 1. 歌曲查询
- 按标题、艺术家、分类、版本查询歌曲
- 按难度等级查询歌曲
- 按标签查询歌曲
- 按谱面特征查询歌曲（转圈、扫键、散打等）

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

## 使用方法

安装完成后，当用户询问舞萌DX相关问题时，skill会自动加载。

### 查询示例：
- "帮我查一下《HOT LIMIT》这首歌的信息"
- "有哪些Master难度13+的歌曲？"
- "东方Project有多少首歌？"
- "舞萌DX版本有哪些新歌？"
- "有哪些有转圈的歌曲？"
- "Master难度有哪些散打谱？"
- "《カゲロウデイズ》有什么谱面特征？"

## 数据更新

如需更新知识库数据，请按以下步骤操作：

### 1. 准备数据文件
将以下文件放在同一目录下：
- `maidata.json` - 原始舞萌DX歌曲数据
- `response.json` - 谱面特征标签数据

### 2. 运行更新脚本
```bash
# 1. 匹配官方ID
python match_ids.py

# 2. 转换数据格式
python convert_maidata.py

# 3. 整合标签数据
python integrate_tags.py

# 4. 生成知识库文件
python generate_kb.py
```

### 3. 重新打包skill
将更新后的 `knowledge_base/` 目录和 `SKILL.md` 重新打包。

## 数据说明

- 总歌曲数：1234首
- 分类数：6个
- 版本数：19个
- 数据来源：diving-fish API
- 谱面特征标签：21种
- 包含谱面特征的歌曲：926首
- 总标签关联数：5384个

### 谱面特征标签说明

**操作类标签**：
- 转圈、扫键、散打、交互、反手、一笔画

**难度类标签**：
- 底力谱、体力谱、高物量、爆发、纵连、跳拍、拆弹

**评价类标签**：
- 水、绝赞段

## 注意事项

1. 数据来源于 diving-fish API，可能与游戏内数据略有差异
2. 部分歌曲可能缺少某些难度谱面
3. 标签是自动生成的，可能不完全准确
4. 宴谱（utage）数据可能不完整
5. 谱面特征标签来源于官方数据，具有较高准确性

## 许可证

本skill仅供学习和个人使用。