# -*- coding: utf-8 -*-
"""
查找重复图片（基于文件MD5哈希）
用法：修改 DIR 为你的图片目录，运行脚本
"""

import hashlib
from pathlib import Path
from collections import defaultdict

# === 配置 ===
DIR = Path(r"D:\photo\SnapBridge")
EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


def main():
    print(f"扫描目录: {DIR}\n")

    hash_map = defaultdict(list)
    scanned = 0

    for f in sorted(DIR.rglob("*")):
        if f.suffix.lower() not in EXTS:
            continue
        scanned += 1
        try:
            h = hashlib.md5(f.read_bytes()).hexdigest()
            hash_map[h].append(f)
        except Exception as e:
            print(f"  [ERR] {f.name}: {e}")

    dups = {h: files for h, files in hash_map.items() if len(files) > 1}

    print(f"扫描完成: {scanned} 个图片文件\n")

    if not dups:
        print("没有找到重复图片。")
        return

    total_waste = 0
    print(f"找到 {len(dups)} 组重复图片：\n")
    for h, files in dups.items():
        sizes = [f.stat().st_size for f in files]
        waste = max(sizes) - min(sizes)
        total_waste += waste
        print(f"  相同内容: {files[0].name} ({len(files)} 份)")
        for f in files:
            size = f.stat().st_size / 1024 / 1024
            print(f"    {f.parent.name}/{f.name}  {size:.1f}MB")
        print()

    print(f"共 {len(dups)} 组重复，可清理 {total_waste/1024/1024:.1f} MB 节省空间。")


if __name__ == "__main__":
    main()
