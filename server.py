import socket
import os
import json
import ffmpeg_helper

# ヘッダーのフォーマットを定義する関数
# JSON長: 2バイト, メディアタイプ長: 1バイト, ペイロード長: 5バイト
def protocol_header(json_length, mediatype_length, payload_length):
    return json_length.to_bytes(2,'big') + mediatype_length.to_bytes(1,'big') + payload_length.to_bytes(5,'big')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9001

# クライアントから受信したファイルを保存するディレクトリ
# ffmpeg_helperモジュール内で処理されたファイルもここに保存される
dpath = 'temp'
if not os.path.exists(dpath):
    os.makedirs(dpath) 

print('Starting up on {} port {}'.format(server_address, server_port))

# SO_REUSEADDR option
# アドレスが既に使用されているというエラーを防ぐ(サーバーを頻繁に起動停止する場合によく起こる)
# TIME-WAIT状態のソケットが残っていてもバインド(再接続)できるようにする
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

sock.bind((server_address,server_port))

sock.listen(1)

while True:
    connection , client_address = sock.accept()

    try:
        print('connection from', client_address)

        header = connection.recv(8)
        json_length = int.from_bytes(header[:2],'big')
        mediatype_length = int.from_bytes(header[2:3],'big')
        payload_length = int.from_bytes(header[3:8],'big')

        json_data = connection.recv(json_length).decode('utf-8')
        mediatype = connection.recv(mediatype_length).decode('utf-8')

        json_dist = json.loads(json_data)

        # 拡張子を含む完全なファイル名を作成
        # 例: filenameが"video1"でmediatypeが".mp4"の場合、完全なファイル名は"video1.mp4"となる
        full_filename = json_dist['filename'] + mediatype

        filepath = os.path.join(dpath, full_filename)

        # ペイロード長を記憶させておいて、1400バイトずつ受信しながらファイルを書き込む
        byte_remaining = payload_length

        with open(filepath,'wb+') as f:
            print(f"Start receiving file from client: {json_dist['filename']}")
            while byte_remaining > 0:
                byte_min = min(1400, byte_remaining)
                data = connection.recv(byte_min)
                f.write(data)
                byte_remaining -= len(data)
        print("Finished receiving file from cliient.")

        action = json_dist['action']

        # ５つのうちのいずれかの処理を実行（"action" , "resize" , "aspect" , "toaudio" , "gif"）
        # クライアント側でこれら以外のアクションが指定されることはない
        if action == 'compress':
            output_file = 'Compressed_' + full_filename
            outpath = os.path.join(dpath,output_file)
            outfile_path = ffmpeg_helper.compression(filepath,outpath)
        elif action == 'resize':
            output_file = 'Resized_' + full_filename
            outpath =  os.path.join(dpath,output_file)
            outfile_path = ffmpeg_helper.resolution_change(filepath,json_dist['width'],json_dist['height'],outpath)
        elif action == 'aspect':
            output_file = 'Aspect_' + full_filename
            outpath =  os.path.join(dpath,output_file)
            outfile_path =ffmpeg_helper.aspect_ratio_change(filepath,json_dist['aspect_ratio'],outpath)
        elif action == 'toaudio':
            output_file = 'Audio_' + os.path.splitext(full_filename)[0] + '.mp3'
            outpath =  os.path.join(dpath,output_file)
            outfile_path =ffmpeg_helper.convert_to_audio(filepath,outpath)
        elif action == 'gif':
            output_file = 'GIF_' + os.path.splitext(full_filename)[0] + '.gif'
            outpath =  os.path.join(dpath,output_file)
            outfile_path =ffmpeg_helper.create_GIF(filepath,json_dist['start_time'],json_dist['duration'],outpath)

        if outfile_path:
            # os.path.basename() でパスを除去し、os.path.splitext() で拡張子を分離
            # 例: "temp/Compressed_video1.mp4" -> "Compressed_video1", ".mp4"
            basename = os.path.basename(outfile_path)
            fn , ext = os.path.splitext(basename)
            filesize = os.path.getsize(outfile_path)
            d = {
                'filename': fn,
            }
            json_data = json.dumps(d).encode('utf-8')
            ext_bits = ext.encode('utf-8')
            header = protocol_header(len(json_data), len(ext_bits), filesize)

            connection.send(header)
            connection.send(json_data)
            connection.send(ext_bits)

            with open(outfile_path,'rb') as f:
                while True:
                    data = f.read(1400)
                    if not data:
                        print("File send completed.")
                        break
                    connection.send(data)
        
        # 処理が終わったら一時ファイルを削除
        try: 
            os.remove(filepath)
            os.remove(outfile_path)
        except FileNotFoundError:
            pass


    finally:
        print("Closing current connection.")
        connection.close()
