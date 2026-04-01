import sys
from moviepy.editor import VideoFileClip
import math
import os

def split_video(input_path, output_dir, segment_length_min=30):
    video = VideoFileClip(input_path)
    total_duration = video.duration  # 秒
    segment_length = segment_length_min * 60
    num_segments = math.ceil(total_duration / segment_length)
    os.makedirs(output_dir, exist_ok=True)
    for i in range(num_segments):
        start_time = i * segment_length
        end_time = min((i + 1) * segment_length, total_duration)
        subclip = video.subclip(start_time, end_time)
        output_filename = os.path.join(output_dir, f"output_{i+1:02d}.mp4")
        print(f"正在导出: {output_filename}")
        subclip.write_videofile(output_filename, codec="libx264", audio_codec="aac")
    print("全部分片完成！")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python split.py <视频文件路径> [输出目录] [每段分钟数，默认30]")
        sys.exit(1)
    input_video_path = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "./splits"
    segment_length_min = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    split_video(input_video_path, output_folder, segment_length_min)