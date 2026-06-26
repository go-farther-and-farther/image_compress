# -*- coding: utf-8 -*-
"""
批量压缩 JPG（有损，重新编码）
"""

from pathlib import Path
from PIL import Image
from multiprocessing import Pool
from functools import partial
Image.MAX_IMAGE_PIXELS = None

# === 配置 ===
INPUT_DIR = Path(r"D:\photo\JPG")
QUALITY = 95           # 目标质量 1-100
MIN_SIZE_MB = 6        # 只处理大于此大小的文件（MB）
KEEP_ORIGINAL = False   # True=保留原图，压缩图加后缀；False=直接覆盖原图
WORKERS = 8


def compress_one(f: Path, quality: int, keep_original: bool):
    if not f.exists():
        return None

    size_kb = f.stat().st_size / 1024

    if keep_original:
        out_path = f.with_name(f.stem + "_compressed" + f.suffix)
    else:
        out_path = f

    try:
        with Image.open(f) as img:
            exif = img.info.get("exif", b"")
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(str(out_path), "JPEG", quality=quality, optimize=True, exif=exif)
    except Exception as e:
        return f.name, 0, 0, 0, str(e)

    new_kb = out_path.stat().st_size / 1024
    saved_kb = size_kb - new_kb
    return f.name, size_kb, new_kb, saved_kb, None


if __name__ == "__main__":
    all_files = sorted(INPUT_DIR.rglob("*.jpg")) + sorted(INPUT_DIR.rglob("*.jpeg"))
    min_bytes = MIN_SIZE_MB * 1024 * 1024
    files = [f for f in all_files if f.stat().st_size > min_bytes]

    print(f"扫描完成：共 {len(all_files)} 个 JPG，>{MIN_SIZE_MB}MB 的有 {len(files)} 个\n")
    for f in files:
        mb = f.stat().st_size / 1024 / 1024
        print(f"  {f.name}  {mb:.1f} MB")

    if not files:
        print("\n没有需要处理的文件。")
    else:
        print(f"\n按回车开始压缩（质量={QUALITY}），按 Ctrl+C 取消...")
        input()

        fn = partial(compress_one, quality=QUALITY, keep_original=KEEP_ORIGINAL)
        total_saved = 0
        processed = 0

        with Pool(WORKERS) as pool:
            for result in pool.imap_unordered(fn, files):
                if result is None:
                    continue
                name, old_kb, new_kb, saved_kb, err = result
                if err:
                    print(f"  [ERR] {name}: {err}")
                    continue
                processed += 1
                total_saved += saved_kb
                print(f"  {name}  {old_kb/1024:.1f}MB -> {new_kb/1024:.1f}MB  节省 {saved_kb/1024:.1f}MB")

        print(f"\n处理 {processed} 张，共节省 {total_saved/1024:.1f} MB")
