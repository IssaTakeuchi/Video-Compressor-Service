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

def compression(input_file, crf=22):

    filename = os.path.basename(input_file)
    output_file = 'compressed_' + filename

    command_line = [
        'ffmpeg',
        '-i', input_file,
        '-vcodec', 'libx265',
        '-crf', str(crf),
        '-y', # 既存のファイルがあった場合に上書きするオプション
        output_file
    ]
    return run_ffmpeg_command(command_line)