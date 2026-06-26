# -*- coding: utf-8 -*-
"""
批量将 PNG 转为 JPG（带压缩，多进程加速）
"""

from pathlib import Path
from PIL import Image
from multiprocessing import Pool
from functools import partial
Image.MAX_IMAGE_PIXELS = None

# === 配置 ===
INPUT_DIR = Path(r"D:\photo\JPG")
QUALITY = 90          # JPG 质量 1-100
DELETE_ORIGINAL = True  # 是否删除原 PNG
WORKERS = 8           # 并行进程数


def convert_one(f: Path, quality: int, delete_original: bool):
    if not f.exists():
        return None
    out_path = f.with_suffix(".jpg")
    if out_path.exists():
        return None  # 已转换，跳过
    with Image.open(f) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")
        w, h = img.size
        img.save(str(out_path), "JPEG", quality=quality)

    size_mb = out_path.stat().st_size / 1024 / 1024
    if delete_original:
        f.unlink()
    return f.name, w, h, size_mb


if __name__ == "__main__":
    files = sorted(INPUT_DIR.rglob("*.png"))
    print(f"找到 {len(files)} 个 PNG，{WORKERS} 进程并行处理")

    fn = partial(convert_one, quality=QUALITY, delete_original=DELETE_ORIGINAL)
    with Pool(WORKERS) as pool:
        for result in pool.imap_unordered(fn, files):
            if result is None:
                continue
            name, w, h, size_mb = result
            print(f"  {name}  {w}x{h}  {size_mb:.1f} MB")

    print("Done.")
