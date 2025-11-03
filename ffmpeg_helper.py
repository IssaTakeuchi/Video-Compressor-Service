import subprocess
import os

def run_ffmpeg_command(command_line):
    try:
        result = subprocess.run(
            command_line,
            check = True,
            capture_output= True,
            text = True)
        print("FFmpeg command executed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing FFmpeg command:")
        print(e.stderr)
        return False

# 動画圧縮
def compression(input_file, outputpath):
    command_line = [
        'ffmpeg',
        '-i', input_file,
        '-vcodec', 'libx265',
        '-crf', '22',
        '-y', # 既存のファイルがあった場合に上書きするオプション
        outputpath
    ]
    if run_ffmpeg_command(command_line) : 
        return outputpath

# 解像度変更
def resolution_change(input_file, width, height,outputpath):
    command_line = [
        'ffmpeg',
        '-i', input_file,
        '-vf', f'scale={width}:{height}',
        '-y', # 既存のファイルがあった場合に上書きするオプション
        outputpath
    ]
    if run_ffmpeg_command(command_line) : 
        return outputpath

# アスペクト比変更
def aspect_ratio_change(input_file, aspect_ratio,outputpath):
    command_line = [
        'ffmpeg',
        '-i', input_file,
        '-aspect', aspect_ratio,
        '-y', # 既存のファイルがあった場合に上書きするオプション
        outputpath
    ]
    if run_ffmpeg_command(command_line) : 
        return outputpath

# 音声変換
def convert_to_audio(input_file,outputpath):
    command_line = [
        'ffmpeg',
        '-i', input_file,
        '-vn', '-ar', '44100', 
        '-ac', '2', 
        '-b:a', '192k',
        '-y', # 既存のファイルがあった場合に上書きするオプション
        outputpath
    ]
    if run_ffmpeg_command(command_line) : 
        return outputpath

# 時間を指定してGIF作成
def create_GIF(input_file, start_time, duration,outputpath):
    command_line = [
        'ffmpeg',
        '-i', input_file,
        '-ss', str(start_time),
        '-t', str(duration),
        '-vf', 'fps=10,scale=320:-1:flags=lanczos',
        '-y', # 既存のファイルがあった場合に上書きするオプション
        outputpath
    ]
    if run_ffmpeg_command(command_line) : 
        return outputpath