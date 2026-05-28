#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成知识库文件 (包含标签信息)
"""

import json
import os
from collections import defaultdict
from typing import Dict, List

def load_data() -> List[Dict]:
    """加载maidata_kb.json"""
    with open('maidata_kb.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_song_markdown(song: Dict) -> str:
    """生成单首歌曲的markdown"""
    md = f"## {song['title']}\n\n"
    md += f"**ID**: {song['id']}\n"
    md += f"**艺术家**: {song['artist']}\n"
    md += f"**分类**: {song['category']}\n"
    md += f"**版本**: {song['version']}\n\n"
    
    # 难度信息
    md += "### 难度信息\n\n"
    
    # 标准谱面
    standard = song['difficulty']['standard']
    if any(standard.values()):
        md += "**标准谱面**:\n"
        md += f"- Basic: {standard.get('basic', '无')}\n"
        md += f"- Advanced: {standard.get('advanced', '无')}\n"
        md += f"- Expert: {standard.get('expert', '无')}\n"
        md += f"- Master: {standard.get('master', '无')}\n"
        md += f"- Re:Master: {standard.get('remaster', '无')}\n\n"
    
    # DX谱面
    dx = song['difficulty']['dx']
    if dx and any(dx.values()):
        md += "**DX谱面**:\n"
        md += f"- Basic: {dx.get('basic', '无')}\n"
        md += f"- Advanced: {dx.get('advanced', '无')}\n"
        md += f"- Expert: {dx.get('expert', '无')}\n"
        md += f"- Master: {dx.get('master', '无')}\n"
        md += f"- Re:Master: {dx.get('remaster', '无')}\n\n"
    
    # 谱面特征标签
    if song.get('chart_tags'):
        md += "### 谱面特征\n\n"
        for difficulty, tags in song['chart_tags'].items():
            md += f"**{difficulty.upper()}**: {', '.join(tags)}\n"
        md += "\n"
    
    # 标签
    if song.get('tags'):
        md += "**标签**: " + ", ".join(song['tags']) + "\n\n"
    
    md += "---\n\n"
    return md

def generate_category_file(category: str, songs: List[Dict], output_dir: str):
    """生成分类文件"""
    # 清理分类名称用于文件名
    clean_category = category.replace('&', 'and').replace('＆', 'and')
    clean_category = clean_category.replace('/', '-').replace('\\', '-')
    clean_category = clean_category.replace('™', '').replace(' ', '_')
    
    filename = f"{clean_category}.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {category}\n\n")
        f.write(f"本分类共有 {len(songs)} 首歌曲\n\n")
        
        # 按版本分组
        versions = defaultdict(list)
        for song in songs:
            versions[song['version']].append(song)
        
        for version, version_songs in sorted(versions.items()):
            f.write(f"## {version} ({len(version_songs)}首)\n\n")
            for song in version_songs:
                f.write(generate_song_markdown(song))
    
    print(f"Generated {filename} with {len(songs)} songs")

def generate_index_file(categories: Dict[str, List[Dict]], output_dir: str):
    """生成索引文件"""
    filepath = os.path.join(output_dir, "INDEX.md")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# 舞萌DX歌曲知识库索引\n\n")
        f.write(f"共有 {sum(len(songs) for songs in categories.values())} 首歌曲\n\n")
        
        # 按版本统计
        versions = defaultdict(list)
        for songs in categories.values():
            for song in songs:
                versions[song['version']].append(song)
        
        f.write("## 按版本分类\n\n")
        for version, songs in sorted(versions.items()):
            f.write(f"- **{version}**: {len(songs)} 首歌曲\n")
        
        f.write("\n## 按分类分类\n\n")
        for category, songs in sorted(categories.items()):
            clean_category = category.replace('&', 'and').replace('＆', 'and')
            clean_category = clean_category.replace('/', '-').replace('\\', '-')
            clean_category = clean_category.replace('™', '').replace(' ', '_')
            f.write(f"- [{category}](./{clean_category}.md): {len(songs)} 首歌曲\n")
        
        # 统计标签信息
        songs_with_tags = 0
        total_tags = 0
        for songs in categories.values():
            for song in songs:
                if song.get('chart_tags'):
                    songs_with_tags += 1
                    total_tags += sum(len(tags) for tags in song['chart_tags'].values())
        
        f.write(f"\n## 谱面特征统计\n\n")
        f.write(f"- 包含谱面特征的歌曲: {songs_with_tags} 首\n")
        f.write(f"- 总标签关联数: {total_tags} 个\n")
        
        # 列出所有标签
        all_tags = set()
        for songs in categories.values():
            for song in songs:
                if song.get('chart_tags'):
                    for tags in song['chart_tags'].values():
                        all_tags.update(tags)
        
        if all_tags:
            f.write(f"\n## 可用的谱面特征标签\n\n")
            for tag in sorted(all_tags):
                f.write(f"- {tag}\n")
        
        # 搜索提示
        f.write("\n## 搜索提示\n\n")
        f.write("可以按以下维度搜索歌曲：\n")
        f.write("- 标题：直接搜索歌曲名称\n")
        f.write("- 艺术家：搜索歌手或乐队名称\n")
        f.write("- 分类：如 '流行&动漫', 'niconico＆VOCALOID™'\n")
        f.write("- 版本：如 '舞萌DX', 'maimai', 'GreeN'\n")
        f.write("- 难度：搜索特定难度等级\n")
        f.write("- 标签：搜索自动生成的标签\n")
        f.write("- 谱面特征：如 '转圈', '扫键', '散打', '交互' 等\n")
    
    print("Generated INDEX.md")

def main():
    print("Loading data...")
    data = load_data()
    
    # 按分类分组
    categories = defaultdict(list)
    for song in data:
        categories[song['category']].append(song)
    
    # 创建输出目录
    output_dir = "knowledge_base"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating knowledge base files in {output_dir}/")
    
    # 生成分类文件
    for category, songs in categories.items():
        generate_category_file(category, songs, output_dir)
    
    # 生成索引文件
    generate_index_file(categories, output_dir)
    
    print(f"\nDone! Generated {len(categories)} category files and INDEX.md")
    print(f"Total songs: {len(data)}")

if __name__ == '__main__':
    main()