import json
import os
import re
import shlex
import shutil
import sys
import time
import base64
import platform
import random
import subprocess
from pathlib import Path

from dotenv import load_dotenv
import requests

load_dotenv(Path(__file__).resolve().parent / ".env")
import yt_dlp
from PIL import Image

import title_unsearch

BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = BASE_DIR / "runtime"
VIDEOS_DIR = RUNTIME_DIR / "videos"
BILIUP_BIN = BASE_DIR / ("biliup.exe" if platform.system() == "Windows" else "biliup")

OWNER_NAME = os.environ.get("U2B_OWNER_NAME", "").strip()
REMOVE_FILE = True  # 是否删除投稿后的视频文件
LineN = "qn" # 线路 cos bda2 qn ws kodo


#从1001track上获取对应的tracklist


def get_double(s):
    return '"' + s + '"'


def cover_webp_to_jpg(webp_path, jpg_path):
    """
    将webp格式的图片转换为jpg格式的图片，并将尺寸扩展至960x650
    :param webp_path: webp格式的图片路径
    :param jpg_path: jpg格式的图片路径
    :return: None
    """
    im = Image.open(webp_path).convert("RGB")
    im = im.resize((960, 650), Image.LANCZOS)
    im.save(jpg_path, "jpeg")
    im.close()


def download(youtube_url, folder_name):
    video_dir = VIDEOS_DIR / str(folder_name)
    video_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        # outtmpl 格式化下载后的文件名，避免默认文件名太长无法保存
        "outtmpl": str(video_dir / "%(id)s.mp4")
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])


def get_info(url):
    ydl_opts = {
        #'proxy': 'http://127.0.0.1:10809',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info


def getVideoPath(id_):
    path = VIDEOS_DIR / str(id_)
    if not path.exists():
        print(f"错误：目录 {path} 不存在")
        return None
    
    for root, dirs, files in os.walk(str(path)):
        for file in files:
            # 查找包含视频ID的文件，优先选择.mp4文件
            if id_ in file and file.endswith('.mp4'):
                return os.path.join(root, file)
            elif id_ in file and file.endswith('.webm'):
                return os.path.join(root, file)
    
    # 如果没找到包含ID的文件，返回第一个视频文件
    for root, dirs, files in os.walk(str(path)):
        for file in files:
            if file.endswith(('.mp4', '.webm', '.mkv', '.avi')):
                return os.path.join(root, file)
    
    print(f"错误：在目录 {path} 中未找到视频文件")
    return None


def download_image(url, id_):
    r = requests.get(url, stream=True)
    cover_path = VIDEOS_DIR / str(id_) / "cover.webp"
    with open(cover_path, "wb") as f:
        # chunk是指定每次写入的大小，每次只写了100kb
        for chunk in r.iter_content(chunk_size=102400):
            if chunk:
                f.write(chunk)


def judge_chs(title):
    for i in title:
        if "\u4e00" <= i <= "\u9fa5":
            return True
    return False


def get_base64(string):
    return str(base64.b64encode(string.encode("utf-8")).decode("utf-8"))


def get_base64_twice(string):
    i = 0
    while i < 2:
        string = get_base64(string)
        i += 1
    return string


def get_chs_title(title):
    while True:
        publish_title = "[大模型音画增强 噪声抑制 底噪去除]"+get_base64(title)
        if len(publish_title) > 80:
            title = title[:-1]
            continue
        else:
            print(publish_title)
            return publish_title


def get_chs_title_twice(title):
    i = 0
    while i < 2:
        title = get_chs_title(title)
        i += 1
    return title


def cut_tags(tags):
    i = 0
    while len(tags) > i:
        if len(tags[i]) > 20:
            tags[i] = tags[i][:20]
        i += 1
    return tags


def main(vUrl, TID, plain_title=True):
    info = get_info(vUrl)
    title = info["title"]
    dynamic_title = title
    author = info["uploader"]
    id_ = info["id"]
    description = info["description"]
    tags = info["tags"]
    print("tags: ", tags)
    cover = info["thumbnail"]
    tags.append(author)
    if OWNER_NAME:
        tags.append(OWNER_NAME)
    
    # init youtube video info

    # Ensure videos directory exists
    videos_dir = VIDEOS_DIR
    videos_dir.mkdir(parents=True, exist_ok=True)

    # Create sub-directory for the specific video
    sub_dir = videos_dir / str(id_)
    try:
        sub_dir.mkdir()
    except FileExistsError:
        shutil.rmtree(sub_dir)
        sub_dir.mkdir()

    download(vUrl, id_)
    download_image(cover, id_)
    cover_webp_to_jpg(str(sub_dir / "cover.webp"), str(sub_dir / "cover.jpg"))

    # if plain_title:
    #     if not judge_chs(title):  # 不包含中文
    #         title = title_unsearch.plain_title(title)
    #     else:
    #         title = get_chs_title_twice(title)
    # title=re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u3040-\u31FF\uFF00-\uFFA0\u0020\u3000])", '', title)

    if len(title) > 80:
        title = title[:80]
    
    # 添加标题前缀并确保总长度不超过80个字符
    title_prefix = "[大模型音画增强 噪声抑制 底噪去除]"
    max_title_length = 80 - len(title_prefix)
    if len(title) > max_title_length:
        title = title[:max_title_length]
    title = title_prefix + title
    
    description = "杜比HIFI 大模型音画增强 噪声抑制 底噪去除 "
    if len(description) > 250:
        description = description[:250]
    if len(tags) > 10:
        tags = tags[:10]
    tags = cut_tags(tags)
    strTags = ",".join(tags)
    videoPath = getVideoPath(id_)
    if videoPath is None:
        raise Exception(f"无法找到视频文件，视频ID: {id_}")
    
    if plain_title:
        vUrl = "YT"
        # description = "-"
    # Ensure paths are correct
    videoPath = os.path.normpath(videoPath)  # 规范化视频文件路径
    coverPath = os.path.normpath(str(sub_dir / "cover.jpg"))  # 规范化封面路径
    cmd_prefix = shlex.quote(str(BILIUP_BIN))

    CMD = (
        cmd_prefix
        + " upload "
        + shlex.quote(videoPath)
        + " --desc "
        + get_double(description)
        + " --copyright 2 "  # 修改为1表示禁止转载
        + "--tag "
        + get_double(strTags)
        + " --tid "
        + str(TID)
        + " --source "
        + get_double(vUrl)
        + " --line "
        + LineN
        + " --dolby 1 "  # 开启杜比音效
        + " --hires 1 "  # 开启高码率
        + " --title "
        + get_double(title)
        + " --cover "
        + shlex.quote(str(sub_dir / "cover.jpg"))
    )
    print("[🚀 Original title]: ", title)
    print("[🚀 Start to using biliup, with these CMD commend]:\n", CMD)
    upload_result = subprocess.run(
        CMD,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    biliupOutput = (upload_result.stdout or "") + (upload_result.stderr or "")
    if biliupOutput.find("投稿成功") == -1:
        if biliupOutput.find("标题相同") == -1:
            print(biliupOutput)
            print(
                "👻 投稿失败.\n👻 解决问题参考 https://github.com/oiov/u2b/issues or https://github.com/ForgQi/biliup-rs/issues "
            )
            exit(1)
        else:
            print("👻 视频标题已存在")
            if REMOVE_FILE:
                shutil.rmtree(sub_dir)
    print("\n🎉🎉🎉 投稿成功，感谢使用哔哩哔哩投稿姬！")
    print("⭐⭐⭐ 如果你觉得小姬姬还不错，那就点个赞吧：https://github.com/oiov/u2b\n")

    if REMOVE_FILE:
        shutil.rmtree(sub_dir)


def mark_url_as_completed(file_path, url):
    """在URL后添加完成标记"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    with open(file_path, 'w') as f:
        for line in lines:
            if line.strip() == url:
                f.write(f"{line.strip()} #COMPLETED\n")
            else:
                f.write(line)


def process_url_file(url_file_path, tid):
    """批量处理URL文件，支持断点续投，自动去重"""
    if not os.path.exists(url_file_path):
        print(f"错误：文件 {url_file_path} 不存在")
        return

    # 读取所有行并去除空行
    with open(url_file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # 统计原始URL数量
    original_count = len(lines)
    
    # 去重并保持原有顺序
    seen = set()
    unique_lines = []
    duplicates = 0
    for line in lines:
        # 去除#COMPLETED标记再比较
        clean_url = line.split(" #COMPLETED")[0].strip()
        if clean_url not in seen:
            seen.add(clean_url)
            unique_lines.append(line)
        else:
            duplicates += 1
    
    # 将去重后的内容写回文件
    with open(url_file_path, 'w') as f:
        for line in unique_lines:
            f.write(line + '\n')
    
    # 过滤出未完成的URL
    urls = []
    skipped = 0
    for line in unique_lines:
        if "#COMPLETED" in line:
            skipped += 1
            continue
        urls.append(line)

    total = len(urls)
    success = 0
    failed = 0

    print(f"\n开始批量处理：")
    print(f"原始URL数量: {original_count}")
    print(f"重复URL数量: {duplicates}")
    print(f"去重后数量: {len(unique_lines)}")
    print(f"待处理数量: {total}（已跳过 {skipped} 个已完成的视频）\n")

    for i, url in enumerate(urls, 1):
        try:
            print(f"\n[{i}/{total}] 处理视频: {url}")
            main(url, tid)
            success += 1
            # 标记当前URL为已完成
            mark_url_as_completed(url_file_path, url)
            
            if i < total:  # 如果不是最后一个视频，则等待
                wait_time = random.randint(50, 65)
                print(f"\n等待 {wait_time} 秒后处理下一个视频...")
                time.sleep(wait_time)
                
        except Exception as e:
            print(f"处理视频 {url} 时出错: {str(e)}")
            failed += 1
            continue

    print(f"\n批量处理完成！")
    print(f"总计: {total} 个视频")
    print(f"成功: {success} 个")
    print(f"失败: {failed} 个")
    print(f"跳过: {skipped} 个（之前已完成）")
    print(f"重复: {duplicates} 个（已自动去重）")

if __name__ == "__main__":
    import random
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube批量搬运+B站投稿工具')
    parser.add_argument('-i', '--input', help='包含YouTube视频URL的文本文件路径')
    parser.add_argument('-t', '--tid', type=int,default=194, help='视频分区ID')
    parser.add_argument('-s', '--single', help='单个视频URL')
    
    args = parser.parse_args()
    
    if args.input:
        process_url_file(args.input, args.tid)
    elif args.single:
        main(args.single, args.tid)
    else:
        parser.print_help()
        exit(1)
    
    exit(0)
