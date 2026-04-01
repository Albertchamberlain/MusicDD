import os
import subprocess
import glob
import shutil
import json
from tqdm import tqdm
import argparse

def get_video_duration(video_path):
    """获取视频时长（秒）"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError):
        return 0

def split_video(video_path, output_dir):
    """将视频分割成30分钟的片段"""
    duration = get_video_duration(video_path)
    if duration <= 1800:  # 如果视频短于30分钟，不需要分割
        return False
        
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_pattern = os.path.join(output_dir, f"{base_name}_part_%d.mp4")
    
    # 计算预计分割片段数
    total_segments = int(duration / 1800) + 1
    
    with tqdm(total=100, desc="分割视频", unit="%") as pbar:
        process = subprocess.Popen(
            [
                'ffmpeg',
                '-i', video_path,
                '-c', 'copy',
                '-map', '0',
                '-segment_time', '1800',
                '-f', 'segment',
                '-reset_timestamps', '1',
                output_pattern
            ],
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # 通过读取ffmpeg输出来更新进度条
        for line in process.stderr:
            if "time=" in line:
                try:
                    time_str = line.split("time=")[1].split()[0]
                    hours, minutes, seconds = map(float, time_str.split(':'))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    progress = min(100, int(current_time / duration * 100))
                    pbar.n = progress
                    pbar.refresh()
                except:
                    continue
        
        process.wait()
        if process.returncode == 0:
            os.remove(video_path)
            return True
        return False

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='批量下载YouTube视频并处理')
    parser.add_argument('-i', '--input', default='urls.txt',
                        help='包含YouTube链接的输入文件路径（默认：urls.txt）')
    parser.add_argument('-o', '--output', default='./downloads',
                        help='视频保存目录（默认：./downloads）')
    parser.add_argument('-s', '--split', action='store_true',
                        help='启用视频分割功能，将超过30分钟的视频分割成多个片段')
    args = parser.parse_args()

    url_file = args.input
    save_dir = args.output

    if not os.path.isfile(url_file):
        print(f'未找到 {url_file}，请先准备好包含YouTube链接的txt文件。')
        return

    os.makedirs(save_dir, exist_ok=True)

    # 读取所有有效的URL
    urls = [line.strip() for line in open(url_file, 'r', encoding='utf-8')
            if line.strip() and not line.strip().startswith('#')]

    # 使用tqdm显示总体下载进度
    for url in tqdm(urls, desc="下载进度", unit="个"):
        print(f'\n正在下载: {url}')
        cmd = [
            'yt-dlp',
            '-c',  # 启用断点续传
            '-f', 'bestvideo+bestaudio',
            '--merge-output-format', 'mp4',
            '--write-thumbnail',
            '-o', os.path.join(save_dir, '%(title)s.%(ext)s'),
            url
        ]
        try:
            # 使用Popen来捕获yt-dlp的输出并显示下载进度
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # 显示yt-dlp的下载进度
            for line in process.stdout:
                if '[download]' in line and '%' in line:
                    print(f'\r{line.strip()}', end='')
            
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
            
            # 获取最新下载的文件
            files = glob.glob(os.path.join(save_dir, '*'))
            if not files:
                continue
                
            latest_files = sorted(files, key=os.path.getctime, reverse=True)
            video_file = next((f for f in latest_files if f.endswith('.mp4')), None)
            
            if video_file:
                # 创建与视频同名的文件夹
                video_name = os.path.splitext(os.path.basename(video_file))[0]
                video_dir = os.path.join(save_dir, video_name)
                os.makedirs(video_dir, exist_ok=True)
                
                # 移动视频文件到目标文件夹
                video_target = os.path.join(video_dir, os.path.basename(video_file))
                shutil.move(video_file, video_target)
                
                # 移动相关的封面文件
                for thumb_ext in ['.jpg', '.webp', '.png']:
                    thumb_file = os.path.splitext(video_file)[0] + thumb_ext
                    if os.path.exists(thumb_file):
                        target_thumb = os.path.join(video_dir, os.path.basename(thumb_file))
                        if thumb_ext == '.webp':
                            from PIL import Image
                            # 将 webp 转换为 jpg
                            img = Image.open(thumb_file).convert('RGB')
                            target_thumb = os.path.splitext(target_thumb)[0] + '.jpg'
                            img.save(target_thumb, 'jpeg')
                            os.remove(thumb_file)  # 删除原始 webp 文件
                        else:
                            shutil.move(thumb_file, target_thumb)
                        break
                
                # 检查是否需要分割视频
                if args.split and split_video(video_target, video_dir):
                    print(f'\n视频已分割为30分钟片段：{video_name}')
                
        except subprocess.CalledProcessError as e:
            print(f'\n下载失败: {url}\n错误信息: {e}')
    print('\n全部下载完成！')

if __name__ == "__main__":
    main()