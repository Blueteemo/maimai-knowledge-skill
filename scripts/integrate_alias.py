#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取别名数据并整合到知识库
"""

import json
import requests
import shutil
from typing import Dict, List

def fetch_alias_data():
    """获取别名数据"""
    url = "https://www.yuzuchan.moe/api/maimaidx/maimaidxalias"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching alias data: {e}")
        return None

def load_maidata() -> List[Dict]:
    """加载歌曲数据"""
    with open('maidata_kb.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_alias_mapping(alias_data: List[Dict]) -> Dict:
    """创建别名映射: song_id -> [aliases]"""
    alias_map = {}
    for item in alias_data:
        song_id = str(item.get('SongID'))
        aliases = item.get('Alias', [])
        if song_id and aliases:
            alias_map[song_id] = aliases
    return alias_map

def integrate_aliases(maidata: List[Dict], alias_map: Dict) -> List[Dict]:
    """整合别名数据"""
    matched = 0
    unmatched = 0
    
    for song in maidata:
        song_id = song['id']
        
        # 初始化别名字段
        song['aliases'] = []
        
        if song_id in alias_map:
            song['aliases'] = alias_map[song_id]
            matched += 1
        else:
            unmatched += 1
    
    print(f"匹配结果: {matched} 首歌曲匹配, {unmatched} 首歌曲未匹配")
    return maidata

def main():
    print("Fetching alias data...")
    alias_response = fetch_alias_data()
    
    if not alias_response or alias_response.get('code') != 0:
        print("Failed to fetch alias data")
        return
    
    alias_data = alias_response.get('content', [])
    print(f"Loaded {len(alias_data)} alias entries")
    
    # 保存原始数据
    with open('alias_data.json', 'w', encoding='utf-8') as f:
        json.dump(alias_data, f, ensure_ascii=False, indent=2)
    print("Saved alias_data.json")
    
    print("Loading maidata...")
    maidata = load_maidata()
    print(f"Loaded {len(maidata)} songs")
    
    print("Creating alias mapping...")
    alias_map = create_alias_mapping(alias_data)
    print(f"Created mapping for {len(alias_map)} songs")
    
    print("Integrating aliases...")
    result = integrate_aliases(maidata, alias_map)
    
    # 统计
    songs_with_aliases = sum(1 for s in result if s['aliases'])
    total_aliases = sum(len(s['aliases']) for s in result)
    
    print(f"\nStatistics:")
    print(f"- Songs with aliases: {songs_with_aliases}")
    print(f"- Total aliases: {total_aliases}")
    
    print("\nSaving result...")
    with open('maidata_kb.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("Done!")
    
    # 移动别名数据到backup
    shutil.move('alias_data.json', 'backup/alias_data.json')
    print("Moved alias_data.json to backup/")

if __name__ == '__main__':
    main()