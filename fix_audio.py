# -*- coding: utf-8 -*-
"""
批量合并视频双声道为单声道（修复相机单边有声问题）
"""

import subprocess
import json
import time
from pathlib import Path
from multiprocessing import Pool

# === 配置 ===
INPUT_DIR = Path(r"C:\Users\LQL\Videos\Radeon ReLive\unknown")
DELETE_ORIGINAL = False  # 处理完是否删除原文件
MERGE_AUDIO = False      # 是否合并双声道为单声道
CRF = 30               # 质量 0-51，越小越清晰越大
PRESET = "medium"       # 编码速度 ultrafast/fast/medium/slow/veryslow
MIN_SIZE_MB = 30       # 最小文件大小（MB）
MAX_SIZE_MB = 10000    # 最大文件大小（MB），超过跳过
MIN_BITRATE_MBPS = 15   # 最小码率（Mbps）
WORKERS = 4


def get_bitrate(f: Path) -> float:
    """获取视频码率（Mbps）"""
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(f)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        data = json.loads(result.stdout)
        return int(data.get("format", {}).get("bit_rate", 0)) / 1_000_000
    except:
        return 0


def fix_one_wrapper(item):
    return fix_one(item[0])


def fix_one(f: Path):
    out_path = f.with_name(f.stem + "_fixed" + f.suffix)
    if out_path.exists():
        return f.name, "跳过（已存在）", 0, 0, 0

    size_mb = f.stat().st_size / 1024 / 1024
    cmd = [
        "ffmpeg", "-y", "-i", str(f),
        "-c:v", "h264_amf", "-qp", str(CRF),
    ]
    if MERGE_AUDIO:
        cmd.extend(["-af", "pan=mono|c0=c0+c1"])
    cmd.extend(["-c:a", "aac", "-b:a", "128k", str(out_path)])

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    elapsed = time.time() - start

    if result.returncode != 0:
        return f.name, f"失败: {result.stderr[-200:]}", 0, 0, 0

    out_mb = out_path.stat().st_size / 1024 / 1024
    ratio = (1 - out_mb / size_mb) * 100 if size_mb > 0 else 0
    if DELETE_ORIGINAL:
        f.unlink()
    return f.name, f"{size_mb:.0f}MB -> {out_mb:.0f}MB  压缩{ratio:.0f}%  {elapsed:.0f}s", size_mb, out_mb, elapsed


if __name__ == "__main__":
    exts = ["*.MOV", "*.mov", "*.MP4", "*.mp4"]
    all_files = []
    for ext in exts:
        all_files.extend(INPUT_DIR.rglob(ext))
    all_files = sorted(set(all_files))

    # 筛选大文件+大码率
    files = []
    for f in all_files:
        size_mb = f.stat().st_size / 1024 / 1024
        if size_mb < MIN_SIZE_MB or size_mb > MAX_SIZE_MB:
            continue
        bitrate = get_bitrate(f)
        if bitrate < MIN_BITRATE_MBPS:
            continue
        files.append((f, size_mb, bitrate))

    print(f"扫描 {len(all_files)} 个视频，>{MIN_SIZE_MB}MB 且 >{MIN_BITRATE_MBPS}Mbps 的有 {len(files)} 个\n")
    for f, size, br in files:
        print(f"  {f.name}  {size:.0f}MB  {br:.0f}Mbps")

    if not files:
        print("\n没有需要处理的文件。")
    else:
        print(f"\n按回车开始（CRF={CRF}, preset={PRESET}），Ctrl+C 取消...")
        input()

        total_saved = 0
        total_time = 0
        processed = 0

        with Pool(WORKERS) as pool:
            for name, status, old_mb, out_mb, elapsed in pool.imap_unordered(fix_one_wrapper, files):
                print(f"  {name}  {status}", flush=True)
                if elapsed > 0:
                    processed += 1
                    total_saved += (old_mb - out_mb)
                    total_time += elapsed

        if processed:
            print(f"\n处理 {processed} 个，共节省 {total_saved:.0f}MB，耗时 {total_time:.0f}s")
        print("Done.")
