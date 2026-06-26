# image_compress

批量图片/视频压缩工具

## 下载

从 [Releases](https://github.com/go-farther-and-farther/image_compress/releases) 下载，解压后得到两个文件：

- `image_compress.exe` — 主程序
- `image_compress_config.json` — 配置文件

## 使用步骤

### 第一步：修改配置

用记事本打开 `image_compress_config.json`，修改以下参数：

```json
{
    "_说明": "修改下面的参数，保存后重新运行程序",
    "input_dir": "D:\\photo\\JPG",
    "_input_dir": "↑ 输入目录路径",
    "quality": 90,
    "_quality": "↑ 压缩质量 1-100，越小文件越小，推荐 85-95",
    "min_size_mb": 4,
    "_min_size_mb": "↑ 只处理大于此大小的文件（MB）",
    "keep_original": true,
    "_keep_original": "↑ true=保留原图，false=直接覆盖原图",
    "convert_png": true,
    "_convert_png": "↑ true=把PNG也转成JPG，false=只压缩JPG",
    "workers": 8,
    "_workers": "↑ 并行处理数量，一般填CPU核心数"
}
```

**必改项：**
- `input_dir`：改成你自己的图片目录路径，例如 `D:\\照片` 或 `C:\\Users\\你的名字\\Pictures`
- 路径中的反斜杠 `\` 要写两个 `\\`

**可选项：**
- `quality`：压缩质量，推荐 85-95，数值越小文件越小
- `min_size_mb`：只压缩大于此大小的文件，避免处理小图
- `keep_original`：建议设为 `true`，保留原图以防万一
- `workers`：并行数量，一般填 CPU 核心数（4/8/16）

### 第二步：运行程序

双击 `image_compress.exe`，程序会：

1. 扫描目录下所有 JPG/PNG 图片
2. 显示符合条件的文件列表
3. 按回车开始压缩
4. 显示每个文件的压缩结果

### 第三步：查看结果

- 如果 `keep_original` 设为 `true`，压缩后的文件会保存在同目录，文件名加 `_compressed` 后缀
- 例如：`照片.jpg` → `照片_compressed.jpg`

## 常见问题

**Q: 路径怎么写？**
A: Windows 路径用 `\\` 双反斜杠，例如 `D:\\photo\\JPG`，不要漏掉盘符（C:、D: 等）

**Q: 压缩后文件变大了怎么办？**
A: 说明原图已经很压缩了，把 `quality` 调大（如 95）或把 `min_size_mb` 调大

**Q: 想直接覆盖原图？**
A: 把 `keep_original` 改为 `false`，**注意：原图会被覆盖，无法恢复**

**Q: 只想压缩 JPG，不想转换 PNG？**
A: 把 `convert_png` 改为 `false`

## 功能列表

| 脚本 | 功能 |
|------|------|
| image_compress.py | 图片压缩主程序（PNG 转 JPG + JPG 压缩） |
| jpg_compress.py | JPG 批量压缩 |
| png2jpg.py | PNG 批量转 JPG |
| fix_audio.py | 视频压缩 + 音频声道合并 |

## 开源协议

MIT License
