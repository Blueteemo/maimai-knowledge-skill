#!/usr/bin/env python3
"""兼容旧生成入口：从已提交快照离线重建，不再依赖缺失的 maidata_kb.json。"""
from update_knowledge_base import SONGS_FILE, load_old_rows, write_snapshot
import json

if __name__ == "__main__":
    write_snapshot(json.loads(SONGS_FILE.read_text(encoding="utf-8")), load_old_rows())
