import socket
import os
import json
import subprocess
import ffmpeg_helper

def protocol_header(json_length, mediatype_length, payload_length):
    return json_length.to_bytes(2,'big') + mediatype_length.to_bytes(1,'big') + payload_length.to_bytes(5,'big')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9001

dpath = 'temp'
if not os.path.exists(dpath):
    os.makedirs(dpath) 

print('Starting up on {} port {}'.format(server_address, server_port))

# SO_REUSEADDR is ON 
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

        full_filename = json_dist['filename'] + mediatype

        filepath = os.path.join(dpath, full_filename)

        byte_remaining = payload_length # Initialized as the remaining number of received bytes

        #  recieve data in 1400 bytes
        with open(filepath,'wb+') as f:
            print(f"Start receiving file from client: {json_dist['filename']}")
            while byte_remaining > 0:
                byte_min = min(1400, byte_remaining)
                data = connection.recv(byte_min)
                f.write(data)
                byte_remaining -= len(data)
        print("Finished receiving file from cliient.")

        action = json_dist['action']

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
        
        try: 
            os.remove(filepath)
            os.remove(outfile_path)
        except FileNotFoundError:
            pass


    finally:
        print("Closing current connection.")
        connection.close()
