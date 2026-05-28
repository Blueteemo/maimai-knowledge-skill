# 舞萌DX歌曲知识库

这是一个包含舞萌DX歌曲数据的知识库，支持opencode skill查询。

## 文件结构

```
knowledge_base/
├── INDEX.md                    # 总索引文件
├── 流行and动漫.md              # 流行&动漫分类
├── niconicoandVOCALOID.md      # niconico＆VOCALOID™分类
├── 舞萌.md                     # 舞萌分类
├── 东方Project.md              # 东方Project分类
├── 其他游戏.md                 # 其他游戏分类
├── 音击-中二节奏.md            # 音击/中二节奏分类
└── README.md                   # 本文件
```

## 数据来源

- 官方数据来源：diving-fish API
- 本地数据处理：maidata.json
- ID映射：id_mapping.json

## 使用方法

### 1. 作为知识库使用
将整个 `knowledge_base/` 目录添加到你的知识库系统中。

### 2. 作为opencode skill使用
skill已安装在 `.opencode/skills/maimai-knowledge/` 目录下。

#### 查询示例：
- "帮我查一下《HOT LIMIT》这首歌的信息"
- "有哪些Master难度13+的歌曲？"
- "东方Project有多少首歌？"
- "舞萌DX版本有哪些新歌？"

## 数据更新

如需更新数据，按以下步骤操作：

1. 更新官方ID映射：
   ```bash
   python match_ids.py
   ```

2. 重新生成JSON数据：
   ```bash
   python convert_maidata.py
   ```

3. 重新生成知识库文件：
   ```bash
   python generate_kb.py
   ```

## 数据字段说明

每首歌曲包含：
- **id**: 官方歌曲ID
- **title**: 歌曲标题
- **artist**: 艺术家
- **category**: 分类
- **version**: 版本
- **difficulty**: 难度信息
  - **standard**: 标准谱面
  - **dx**: DX谱面
  - **utage**: 宴谱
- **tags**: 自动生成的标签

## 注意事项

1. 数据来源于 diving-fish API，可能与游戏内数据略有差异
2. 部分歌曲可能缺少某些难度谱面
3. 标签是自动生成的，可能不完全准确
4. 宴谱（utage）数据可能不完整

## 统计信息

- 总歌曲数：1234首
- 分类数：6个
- 版本数：19个

## 相关文件

- `maidata_kb.json`: 完整的JSON格式数据
- `official_music_data.json`: 官方原始数据
- `id_mapping.json`: 本地索引到官方ID的映射