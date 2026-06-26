# -*- coding: utf-8 -*-
"""
批量图片压缩工具（PNG转JPG + JPG压缩）
读取同目录下 image_compress_config.json 配置
"""

import json
import sys
from pathlib import Path
from PIL import Image
from multiprocessing import Pool
from functools import partial
Image.MAX_IMAGE_PIXELS = None

# 读取配置
SCRIPT_DIR = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).parent
CONFIG_PATH = SCRIPT_DIR / "image_compress_config.json"

DEFAULT_CONFIG = {
    "input_dir": "D:\\photo\\JPG",
    "quality": 90,
    "min_size_mb": 4,
    "keep_original": True,
    "convert_png": True,
    "workers": 8
}

if not CONFIG_PATH.exists():
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
    print(f"已生成默认配置: {CONFIG_PATH}")
    print("请修改配置后重新运行。")
    sys.exit(0)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

INPUT_DIR = Path(config["input_dir"])
QUALITY = config.get("quality", 90)
MIN_SIZE_MB = config.get("min_size_mb", 4)
KEEP_ORIGINAL = config.get("keep_original", True)
CONVERT_PNG = config.get("convert_png", True)
WORKERS = config.get("workers", 8)


def process_one(f: Path, quality: int, keep_original: bool, convert_png: bool):
    if not f.exists():
        return None

    size_kb = f.stat().st_size / 1024
    is_png = f.suffix.lower() == ".png"

    # PNG 转 JPG
    if is_png and convert_png:
        if keep_original:
            out_path = f.with_name(f.stem + "_converted.jpg")
        else:
            out_path = f.with_suffix(".jpg")
        try:
            with Image.open(f) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(str(out_path), "JPEG", quality=quality, optimize=True)
        except Exception as e:
            return f.name, 0, 0, 0, str(e)
        new_kb = out_path.stat().st_size / 1024
        saved_kb = size_kb - new_kb
        return f.name, size_kb, new_kb, saved_kb, None

    # JPG 压缩
    if not is_png:
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

    return None


if __name__ == "__main__":
    all_png = sorted(INPUT_DIR.rglob("*.png")) if CONVERT_PNG else []
    all_jpg = sorted(INPUT_DIR.rglob("*.jpg")) + sorted(INPUT_DIR.rglob("*.jpeg"))
    all_files = sorted(set(all_png + all_jpg))

    min_bytes = MIN_SIZE_MB * 1024 * 1024
    files = [f for f in all_files if f.stat().st_size > min_bytes]

    print(f"配置: {CONFIG_PATH}")
    print(f"  目录: {INPUT_DIR}")
    print(f"  质量: {QUALITY}")
    print(f"  最小: {MIN_SIZE_MB}MB")
    print(f"  保留原图: {KEEP_ORIGINAL}")
    print(f"  PNG转JPG: {CONVERT_PNG}")
    print()
    print(f"扫描完成: 共 {len(all_files)} 个文件, >{MIN_SIZE_MB}MB 的有 {len(files)} 个\n")
    for f in files:
        mb = f.stat().st_size / 1024 / 1024
        print(f"  {f.name}  {mb:.1f} MB")

    if not files:
        print("\n没有需要处理的文件。")
    else:
        print(f"\n按回车开始压缩, Ctrl+C 取消...")
        input()

        fn = partial(process_one, quality=QUALITY, keep_original=KEEP_ORIGINAL, convert_png=CONVERT_PNG)
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

        print(f"\n处理 {processed} 个, 共节省 {total_saved/1024:.1f} MB")
