# 🎵 舞萌DX歌曲知识库 — maimai-knowledge-skill

舞萌DX（Maimai DX）歌曲知识库，支持歌曲查询、谱面分析、实时查分、封面图获取和拟合难度查询。

## 文件结构

```
maimai-knowledge-skill/
├── SKILL.md                    # Skill 定义文件（OpenCode / AstrBot 集成）
├── README.md                   # 本文件
├── .gitignore                  # Git 忽略规则
├── level_index.json            # 难度索引（1233首歌，按14个等级分类）
├── knowledge_base/             # 知识库文件
│   ├── INDEX.md                # 总索引
│   ├── README.md               # 知识库说明
│   ├── 流行and动漫.md          # 流行 & 动漫分类
│   ├── niconicoandVOCALOID.md  # niconico ＆ VOCALOID™ 分类
│   ├── 舞萌.md                 # 舞萌分类
│   ├── 东方Project.md          # 东方Project分类
│   ├── 其他游戏.md             # 其他游戏分类
│   └── 音击-中二节奏.md        # 音击/中二节奏分类
└── scripts/                    # 工具脚本
    ├── maimai_lookup.py        # 玩家查分脚本（基于 maimai-py SDK）
    ├── maimai_utils.py         # 封面图 & 拟合难度工具
    ├── match_ids.py            # 官方ID匹配脚本
    ├── convert_maidata.py      # 数据转换脚本
    ├── integrate_alias.py      # 别名整合脚本
    ├── integrate_tags.py       # 标签整合脚本
    └── generate_kb.py          # 知识库生成脚本
```

## 功能特性

### 🎮 玩家查分
- 通过 QQ 号或水鱼用户名查询玩家 B50 成绩
- 支持查 Rating、B35/B15 分数、谱面达成率、DX评分、FC/FS状态
- 数据源：水鱼查分器（DivingFish）
- 依赖安装：`pip install maimai-py`
- 快速使用：`python scripts/maimai_lookup.py <QQ号或用户名>`

### 🖼️ 封面图获取
- 通过歌曲ID获取水鱼封面PNG
- 自动处理ID补零规则（10001~11000区间需减10000后补零）
- 宴谱无封面图

### 📊 拟合难度查询
- 查询谱面拟合定数、平均达成率、样本量
- 数据源：水鱼 `/chart_stats` API（无需开发者Token）

### 🔍 歌曲查询
- 按标题、艺术家、分类、版本查询歌曲
- 按难度等级（1~14）查询歌曲
- 按标签、谱面特征查询歌曲

### 📈 难度分析与统计
- 查询歌曲的标准谱面和DX谱面难度
- 按分类、版本统计歌曲数量
- 谱面特征统计（21种标签，926首含标签歌曲）

## 安装方法

### 作为 AstrBot Skill 安装

```bash
git clone https://github.com/Blueteemo/maimai-knowledge-skill.git
# 将 maimai-knowledge-skill 目录放到 AstrBot 的 skills 目录下
# 重启 AstrBot 即可自动加载
```

### 依赖安装

```bash
pip install maimai-py requests
```

## 使用示例

- "帮我查一下《HOT LIMIT》这首歌的信息"
- "有哪些Master难度13+的歌曲？"
- "东方Project有多少首歌？"
- "有哪些有转圈的歌曲？"
- "查一下B50"（需提供QQ号或水鱼用户名）
- "这首曲子拟合难度多少？"（需提供歌曲ID）

## 数据说明

- 总歌曲数：1234首
- 分类数：6个
- 版本数：19个
- 谱面特征标签：21种
- 包含谱面特征的歌曲：926首
- 总标签关联数：5384个
- 数据来源：Diving-Fish API

## 许可证

本仓库仅供学习和个人使用。
