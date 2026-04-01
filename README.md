<!-- markdownlint-disable MD033 MD041 -->
<div align="center">

<pre>
======================================================================
   *   *   *      *   *   *      *   *   *      *   *   *
  /|\ /|\ /|\    /|\ /|\ /|\    /|\ /|\ /|\    /|\ /|\ /|\
 / | V | V | \  / | V | V | \  / | V | V | \  / | V | V | \
======================================================================

 __  __           _
|  \/  | ___   __| |
| |\/| |/ _ \ / _` |
| |  | | (_) | (_| |
|_|  |_|\___/ \__,_|

 ____    ____
|  _ \  |  _ \
| | | | | | | |
| |_| | | |_| |
|____/  |____/

======================================================================
</pre>

**YouTube → Bilibili 工作流与批量工具集**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](u2b/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-3776ab.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Albertchamberlain/MusicDD/pulls)

[简介](#简介) · [功能特性](#功能特性) · [仓库结构](#仓库结构) · [快速开始](#快速开始) · [相关说明](#相关说明) · [贡献与协议](#贡献与协议)

</div>

---

## 简介

**MusicDD** 是个人音乐 / 视频搬运与批处理相关脚本集合：从 YouTube 下载、长视频切片，到通过 [biliup](https://github.com/biliup/biliup) 投稿 B 站；并包含可复用的艺人链接清单（`Arts/`）与独立子项目示例。

> 名称里的 **DD** 取自 **D**ownload & **D**eliver（下载与投递），也呼应「音乐向」内容管线。

---

## 功能特性

| 模块 | 说明 |
|------|------|
| **`u2b/`** | YouTube 下载 + 封面处理 + **B 站自动投稿**；支持单条、批量、断点续传（见子目录 README） |
| **`batch_yt_download.py`** | 批量 `yt-dlp` 下载；可选 **`--split`** 用 **ffmpeg** 将超过 30 分钟的视频切段（内置 `split_video`，依赖 `ffmpeg` / `ffprobe`） |
| **`split.py`** | 独立脚本：用 **MoviePy** 将长视频按固定时长切片（命令行传入视频路径；与 `batch_yt_download` 无 import 关系） |
| **`Arts/`** | 各艺人 / 主题的 URL 列表文本，便于批量任务复用 |
| **`bilibili-viewcount-booster/`** | 第三方「播放量」实验性子项目（代理轮询）；**请自行评估合规与平台规则后再使用** |

---

## 仓库结构

```text
MusicDD/
├── README.md                 # 本说明
├── .gitignore
├── batch_yt_download.py      # 批量下载 YouTube（可选分割）
├── split.py
├── Arts/                     # 艺人/主题 URL 列表
├── u2b/                      # YouTube → Bilibili 主流程
│   ├── new_downloader.py
│   ├── task_manager.py
│   ├── requirements.txt
│   ├── setup.sh / start.sh
│   └── README.md             # u2b 详细文档（参数、分区 TID 等）
└── bilibili-viewcount-booster/
    ├── booster.py
    └── README.md
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Albertchamberlain/MusicDD.git
cd MusicDD
```

### 2. 仅批量下载 YouTube（根目录脚本）

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install tqdm pillow    # batch_yt_download 会用到 Pillow（缩略图 webp→jpg）

# 准备 urls.txt，每行一个链接，然后：
python3 batch_yt_download.py -i urls.txt -o ./downloads

# 长视频按 30 分钟切段：
python3 batch_yt_download.py -i urls.txt -o ./downloads --split
```

需本机已安装 **`yt-dlp`**、**`ffmpeg`** / **`ffprobe`**。

### 3. YouTube → Bilibili（`u2b/`）

```bash
cd u2b
# 按 u2b/README.md：setup.sh、biliup login、配置 OWNER / 线路等
python3 new_downloader.py -s "https://www.youtube.com/watch?v=VIDEO_ID" -t 21
```

完整参数、分区 TID、断点续传格式等见 **[`u2b/README.md`](u2b/README.md)**。

---

## 相关说明

- **Cookie / 登录信息**：请勿将 `cookies.json` 等敏感文件提交到 Git；本仓库 `.gitignore` 已尽量排除常见密钥与虚拟环境目录。
- **合规**：请遵守 YouTube、哔哩哔哩及当地法律与平台服务条款；自动化投稿与播放量相关工具可能受平台限制，风险自负。
- **依赖致谢**：[yt-dlp](https://github.com/yt-dlp/yt-dlp)、[biliup](https://github.com/biliup/biliup)、[Pillow](https://python-pillow.org/) 等。

---

## 贡献与协议

欢迎 Issue / PR。子目录 **`u2b/`** 与 **`bilibili-viewcount-booster/`** 各有 LICENSE；`u2b` 默认 **MIT**（以该目录内 `LICENSE` 为准）。

---

<div align="center">

<sub>如果这个项目对你有帮助，可以考虑点个 Star</sub>

</div>
