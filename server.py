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
            output_file = ffmpeg_helper.compression(filepath)
        elif action == 'resize':
            output_file = ffmpeg_helper.resolution_change(filepath,json_dist['width'],json_dist['height'])
        elif action == 'aspect':
            output_file =ffmpeg_helper.aspect_ratio_change(filepath,json_dist['aspect_ratio'])
        elif action == 'toaudio':
            output_file =ffmpeg_helper.convert_to_audio(filepath)
        elif action == 'gif':
            output_file =ffmpeg_helper.create_GIF(filepath,json_dist['start_time'],json_dist['duration'])

        if output_file:
            fn , ext = os.path.splitext(output_file)
            filesize = os.path.getsize(output_file)
            d = {
                'filename': fn,
            }
            json_data = json.dumps(d).encode('utf-8')
            ext_bits = ext.encode('utf-8')
            header = protocol_header(len(json_data), len(ext_bits), filesize)

            connection.send(header)
            connection.send(json_data)
            connection.send(ext_bits)

            with open(output_file,'rb') as f:
                while True:
                    data = f.read(1400)
                    if not data:
                        break
                    connection.send(data) 


    finally:
        print("Closing current connection.")
        connection.close()
