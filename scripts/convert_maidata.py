#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert maidata.json to a knowledge base friendly format.
"""

import json
import re
from typing import Any, Dict, List, Optional

def generate_tags(song: Dict[str, Any]) -> List[str]:
    """Generate tags from song data."""
    tags = set()
    
    # Add artist as tag (split by common separators)
    artist = song.get('artist', '')
    if artist:
        # Split by common separators: /, ／, feat., &, ×, ・, 「, 」, etc.
        # Simple approach: split by non-alphanumeric characters (except CJK)
        # For now, just add the whole artist string and some common splits
        tags.add(artist)
        # Split by common Japanese/Chinese separators
        for sep in ['/', '／', 'feat.', '＆', '&', '×', '・', '「', '」', '（', '）', '(', ')', 'CV:', 'CV：']:
            if sep in artist:
                parts = artist.split(sep)
                for part in parts:
                    part = part.strip()
                    if part:
                        tags.add(part)
    
    # Add category
    category = song.get('category', '')
    if category:
        tags.add(category)
        # Split category by '＆' or '&'
        for sep in ['＆', '&']:
            if sep in category:
                parts = category.split(sep)
                for part in parts:
                    part = part.strip()
                    if part:
                        tags.add(part)
    
    # Add version
    version = song.get('version', '')
    if version:
        tags.add(version)
    
    # Remove empty strings and duplicates
    tags = {tag for tag in tags if tag}
    return sorted(tags)

def extract_difficulty(song: Dict[str, Any]) -> Dict[str, Any]:
    """Extract difficulty fields into nested structure."""
    standard = {}
    dx = {}
    
    # Standard difficulty fields (lev_*)
    for level in ['bas', 'adv', 'exp', 'mas', 'remas']:
        key = f'lev_{level}'
        if key in song:
            standard[level if level != 'remas' else 'remaster'] = song[key]
    
    # DX difficulty fields (dx_lev_*)
    for level in ['bas', 'adv', 'exp', 'mas', 'remas']:
        key = f'dx_lev_{level}'
        if key in song:
            dx[level if level != 'remas' else 'remaster'] = song[key]
    
    # Ensure all keys exist (set to None if missing)
    for level in ['basic', 'advanced', 'expert', 'master', 'remaster']:
        if level not in standard:
            # Map from short names
            if level == 'basic':
                standard.setdefault(level, standard.pop('bas', None))
            elif level == 'advanced':
                standard.setdefault(level, standard.pop('adv', None))
            elif level == 'expert':
                standard.setdefault(level, standard.pop('exp', None))
            elif level == 'master':
                standard.setdefault(level, standard.pop('mas', None))
            elif level == 'remaster':
                standard.setdefault(level, standard.pop('remas', None))
    
    for level in ['basic', 'advanced', 'expert', 'master', 'remaster']:
        if level not in dx:
            if level == 'basic':
                dx.setdefault(level, dx.pop('bas', None))
            elif level == 'advanced':
                dx.setdefault(level, dx.pop('adv', None))
            elif level == 'expert':
                dx.setdefault(level, dx.pop('exp', None))
            elif level == 'master':
                dx.setdefault(level, dx.pop('mas', None))
            elif level == 'remaster':
                dx.setdefault(level, dx.pop('remas', None))
    
    # If no DX difficulty, set to None
    if not any(dx.values()):
        dx = None
    
    return {
        'standard': standard,
        'dx': dx,
        'utage': None  # No utage data in current file
    }

def convert_song(song: Dict[str, Any], song_id: int) -> Dict[str, Any]:
    """Convert a single song entry."""
    # Generate tags
    tags = generate_tags(song)
    
    # Extract difficulty
    difficulty = extract_difficulty(song)
    
    # Build new song structure
    new_song = {
        'id': song_id,
        'title': song.get('title', ''),
        'artist': song.get('artist', ''),
        'category': song.get('category', ''),
        'image_file': song.get('image_file', ''),
        'difficulty': difficulty,
        'version': song.get('version', ''),
        'tags': tags
    }
    
    return new_song

def main():
    input_file = 'maidata.json'
    output_file = 'maidata_kb.json'
    mapping_file = 'id_mapping.json'
    
    # Load ID mapping
    print(f"Loading ID mapping from {mapping_file}...")
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            id_mapping = json.load(f)
        print(f"Loaded {len(id_mapping)} mappings")
    except FileNotFoundError:
        print(f"Warning: {mapping_file} not found, using sequential IDs")
        id_mapping = {}
    
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Converting {len(data)} songs...")
    converted = []
    for idx, song in enumerate(data):
        # Get official ID from mapping, fallback to sequential ID
        official_id = id_mapping.get(str(idx))
        if official_id:
            song_id = official_id
        else:
            song_id = str(idx + 1)  # Fallback to 1-based sequential ID
        
        converted_song = convert_song(song, song_id)
        converted.append(converted_song)
    
    print(f"Writing {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)
    
    print("Done!")
    
    # Print sample
    print("\nSample (first song):")
    print(json.dumps(converted[0], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()