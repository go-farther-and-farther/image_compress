# image_compress

批量图片/视频压缩工具

## 功能

- **image_compress.py** — 图片压缩主程序（PNG 转 JPG + JPG 压缩）
- **jpg_compress.py** — JPG 批量压缩
- **png2jpg.py** — PNG 批量转 JPG
- **fix_audio.py** — 视频压缩 + 音频声道合并

## 使用方法

### 直接运行

```bash
pip install Pillow
python image_compress.py
```

### 打包 exe

```bash
build.bat
```

### 配置

编辑 `image_compress_config.json`：

```json
{
    "input_dir": "D:\\photo\\JPG",
    "quality": 90,
    "min_size_mb": 4,
    "keep_original": true,
    "convert_png": true,
    "workers": 8
}
```

## 下载

从 [Releases](https://github.com/go-farther-and-farther/image_compress/releases) 下载 exe。
