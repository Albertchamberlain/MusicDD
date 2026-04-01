
# YouTube to Bilibili 自动搬运工具

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个强大的 YouTube 视频自动搬运到 B 站的工具，支持批量处理、断点续传、自定义分区等功能。

---

## ✨ 特性

- 🚀 一键下载 YouTube 视频并自动投稿到 B 站
- 📦 支持批量处理多个视频链接
- 🔄 断点续传功能，支持中断后继续投稿
- 🎵 自动处理视频封面（webp 转 jpg）
- 🎨 支持自定义视频分区
- ⏱️ 智能延时功能，避免频繁投稿
- 🔊 支持杜比音效和高码率设置
- 🎯 自动优化标题和描述

---

## 🛠️ 安装

### 前置要求

- Python 3.6+
- biliup 命令行工具
- 稳定的网络连接

### 安装步骤

1. 克隆项目：

   ```bash
   git clone https://github.com/oiov/u2b.git
   cd u2b
   ```
2. 安装依赖：

   ```bash
   sudo bash setup.sh
   ```
3. 登录 B 站账号：

   ```bash
   ./biliup login
   ```

---

## ⚙️ 配置

1. **敏感信息只放在本地（勿提交 Git）**

   - `cookies.json`：由 `biliup login` 生成，**已在 `.gitignore` 中忽略**。
   - 在 `u2b` 目录复制环境变量模板并填写：
     ```bash
     cp .env.example .env
     ```
   - `.env` 中需要配置（`task_manager` 必填）：
     - `BILI_OWNER_UID`：你的 B 站 mid（数字 UID）
     - `BILI_MSG_BEGIN_SEQNO`：私信接口 `fetch_session_msgs` 的 `begin_seqno` 游标
   - 可选：`U2B_OWNER_NAME` — 投稿标签中追加的展示名；不填则不加该标签。

2. （可选）调整投稿参数：

   - 修改 `new_downloader.py` 中 `LineN` 选择上传线路（可选：cos/bda2/qn/ws/kodo）
   - 设置 `REMOVE_FILE` 控制是否在投稿后删除本地文件
   - 运行时文件统一在 `runtime/`（`videos/`、`task_work.log`、任务历史等）

---

## 📝 使用方法

### 单个视频投稿

```bash
python3 new_downloader.py -s "https://www.youtube.com/watch?v=xxxxxx" -t 21
```

### 批量投稿

1. 准备 URL 文件（如 `urls.txt`）：

   ```bash
   https://www.youtube.com/watch?v=xxxxx
   https://www.youtube.com/watch?v=yyyyy
   https://www.youtube.com/watch?v=zzzzz
   ```

2. 执行批量投稿

```shell
python3 new_downloader.py -i urls.txt -t 21
```

### 目录说明（重构后）

- `assets/images/`：封面与展示素材
- `runtime/`：运行时产物（自动创建，默认不入库）


### 参数说明

* `-s, --single` ：单个视频 URL
* `-i, --input` ：包含多个视频 URL 的文件路径
* `-t, --tid` ：视频分区 ID（默认：194 即电子音乐分区）


### 分区 ID 参考

* 知识区：
  * 科学科普：201
  * 社科法律心理：124
  * 人文历史：228
  * 财经商业：207
  * 校园学习：208
  * 职业职场：209
  * 设计创意：229
  * 野生技能协会：122


## 🔄 断点续传

支持在投稿过程中断后继续上传：

1. URL 文件中已完成的视频会被标记：

   **Copy**

   ```
   https://www.youtube.com/watch?v=xxxxx
   #COMPLETED
   https://www.youtube.com/watch?v=yyyyy
   ```
2. 重新运行时会自动跳过已完成的视频

---

## 📊 投稿进度

* 显示当前处理进度和统计信息
* 支持显示成功/失败/跳过的视频数量
* 每个视频处理后自动等待 30-45 秒

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📜 开源协议

本项目基于 MIT 协议开源，详见 LICENSE 文件。

---

## 🙏 致谢

* [biliup](https://github.com/biliup/biliup) - B站命令行投稿工具
* [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube视频下载工具
