#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合标签数据到maidata_kb.json (通过歌曲标题匹配)
"""

import json
from typing import Dict, List

def load_tags_data() -> Dict:
    """加载标签数据"""
    with open('response.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_maidata() -> List[Dict]:
    """加载歌曲数据"""
    with open('maidata_kb.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_tag_mapping(tags_data: Dict) -> Dict:
    """创建标签映射"""
    # 标签ID -> 标签信息
    tag_map = {}
    for tag in tags_data['tags']:
        tag_map[tag['id']] = {
            'name': tag['localized_name']['zh-Hans'],
            'description': tag['localized_description']['zh-Hans'],
            'group_id': tag['group_id']
        }
    
    # 分组ID -> 分组信息
    group_map = {}
    for group in tags_data['tagGroups']:
        group_map[group['id']] = {
            'name': group['localized_name']['zh-Hans'],
            'color': group['color']
        }
    
    return tag_map, group_map

def create_song_tags_mapping(tags_data: Dict) -> Dict:
    """创建歌曲标签映射 (通过歌曲标题)"""
    # song_title -> {difficulty -> [tag_names]}
    song_tags = {}
    
    for tag_song in tags_data['tagSongs']:
        song_title = str(tag_song['song_id'])  # 这里实际上是歌曲标题
        difficulty = tag_song['sheet_difficulty']
        tag_id = tag_song['tag_id']
        
        if song_title not in song_tags:
            song_tags[song_title] = {}
        if difficulty not in song_tags[song_title]:
            song_tags[song_title][difficulty] = []
        
        song_tags[song_title][difficulty].append(tag_id)
    
    return song_tags

def integrate_tags(maidata: List[Dict], tags_data: Dict) -> List[Dict]:
    """整合标签数据到歌曲数据"""
    tag_map, group_map = create_tag_mapping(tags_data)
    song_tags = create_song_tags_mapping(tags_data)
    
    # 统计匹配情况
    matched = 0
    unmatched = 0
    
    for song in maidata:
        song_title = song['title']
        
        # 初始化标签字段
        song['chart_tags'] = {}
        
        if song_title in song_tags:
            matched += 1
            # 为每个难度添加标签
            for difficulty, tag_ids in song_tags[song_title].items():
                tag_names = []
                for tag_id in tag_ids:
                    if tag_id in tag_map:
                        tag_names.append(tag_map[tag_id]['name'])
                
                if tag_names:
                    song['chart_tags'][difficulty] = tag_names
        else:
            unmatched += 1
        
        # 将所有标签添加到tags字段
        all_tags = set(song.get('tags', []))
        for difficulty_tags in song['chart_tags'].values():
            all_tags.update(difficulty_tags)
        song['tags'] = sorted(list(all_tags))
    
    print(f"匹配结果: {matched} 首歌曲匹配, {unmatched} 首歌曲未匹配")
    
    return maidata

def main():
    print("Loading tags data...")
    tags_data = load_tags_data()
    print(f"Loaded {len(tags_data['tags'])} tags, {len(tags_data['tagGroups'])} groups, {len(tags_data['tagSongs'])} song-tag associations")
    
    print("Loading maidata...")
    maidata = load_maidata()
    print(f"Loaded {len(maidata)} songs")
    
    print("Integrating tags...")
    result = integrate_tags(maidata, tags_data)
    
    # 统计
    songs_with_tags = sum(1 for s in result if s['chart_tags'])
    total_associations = sum(len(tags) for s in result for tags in s['chart_tags'].values())
    
    print(f"\nStatistics:")
    print(f"- Songs with chart tags: {songs_with_tags}")
    print(f"- Total tag associations: {total_associations}")
    
    print("\nSaving result...")
    with open('maidata_kb.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("Done!")

if __name__ == '__main__':
    main()