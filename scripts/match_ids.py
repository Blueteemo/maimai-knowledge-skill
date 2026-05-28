#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Match official IDs from diving-fish API with local maidata.json
"""

import json
import requests
from typing import Dict, List, Optional

def fetch_official_data() -> List[Dict]:
    """Fetch official music data from diving-fish API"""
    url = "https://www.diving-fish.com/api/maimaidxprober/music_data"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching official data: {e}")
        return []

def load_local_data() -> List[Dict]:
    """Load local maidata.json"""
    with open('maidata.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def find_matching_id(local_song: Dict, official_data: List[Dict]) -> Optional[str]:
    """Find matching official ID for a local song"""
    local_title = local_song.get('title', '').strip()
    local_artist = local_song.get('artist', '').strip()
    
    # Try exact match first
    for official in official_data:
        official_title = official.get('title', '').strip()
        official_artist = official.get('basic_info', {}).get('artist', '').strip()
        
        if official_title == local_title and official_artist == local_artist:
            return official['id']
    
    # Try fuzzy match (title only)
    for official in official_data:
        official_title = official.get('title', '').strip()
        if official_title == local_title:
            # Check if artist is similar
            official_artist = official.get('basic_info', {}).get('artist', '').strip()
            if local_artist in official_artist or official_artist in local_artist:
                return official['id']
    
    # Try even fuzzier match (ignore case and special characters)
    import re
    def clean_text(text: str) -> str:
        return re.sub(r'[^\w\s]', '', text.lower()).strip()
    
    clean_local_title = clean_text(local_title)
    for official in official_data:
        official_title = official.get('title', '').strip()
        if clean_text(official_title) == clean_local_title:
            return official['id']
    
    return None

def main():
    print("Fetching official data...")
    official_data = fetch_official_data()
    if not official_data:
        print("Failed to fetch official data")
        return
    
    print(f"Loaded {len(official_data)} official songs")
    
    print("Loading local data...")
    local_data = load_local_data()
    print(f"Loaded {len(local_data)} local songs")
    
    # Create mapping
    mapping = {}
    matched = 0
    unmatched = 0
    
    for i, local_song in enumerate(local_data):
        official_id = find_matching_id(local_song, official_data)
        if official_id:
            mapping[i] = official_id
            matched += 1
        else:
            mapping[i] = None
            unmatched += 1
            try:
                print(f"Unmatched: {local_song.get('title', 'Unknown')} - {local_song.get('artist', 'Unknown')}")
            except UnicodeEncodeError:
                print(f"Unmatched: [title with special chars] - [artist with special chars]")
    
    print(f"\nResults: {matched} matched, {unmatched} unmatched")
    
    # Save mapping
    with open('id_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    print("Mapping saved to id_mapping.json")
    
    # Also save official data for reference
    with open('official_music_data.json', 'w', encoding='utf-8') as f:
        json.dump(official_data, f, ensure_ascii=False, indent=2)
    
    print("Official data saved to official_music_data.json")

if __name__ == '__main__':
    main()