import socket
import os
import json
import subprocess
import ffmpeg_helper

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

        # receive filesize
        header = connection.recv(8)
        json_length = int.from_bytes(header[:2],'big')
        mediatype_length = int.from_bytes(header[2:3],'big')
        payload_length = int.from_bytes(header[3:8],'big')

        json_data = connection.recv(json_length).decode('utf-8')
        mediatype = connection.recv(mediatype_length).decode('utf-8')
        payload_size = connection.recv(payload_length).decode('utf-8')

        # convert string into int
        filesize = int(payload_size)

        json_dist = json.loads(json_data)

        action = json_dist['action']
        filepath = os.path.join(dpath,json_dist['filename'])

        if action == 'compress':
            ffmpeg_helper.compression(filepath)
        elif action == 'resize':
            ffmpeg_helper.resolution_change(filepath,json_dist['width'],json_dist['height'])
        elif action == 'aspect':
            ffmpeg_helper.aspect_ratio_change(filepath,json_dist['aspect_ratio'])
        elif action == 'toaudio':
            ffmpeg_helper.convert_to_audio(filepath)
        elif action == 'gif':
            ffmpeg_helper.create_GIF(filepath,json_dist['start_time'],json_dist['duration'])

        # check filesize and send status 1(smaller) or 2(larger)
        if filesize < pow(2,40):
            status = 1
            status_bytes = str(status).encode('utf-8')
            connection.sendall(status_bytes)

            #  recieve data in 1400 bytes
            with open(os.path.join(dpath,payload_length),'wb+') as f:
                while filesize > 0:
                    data = connection.recv(1400)
                    f.write(data)
                    filesize -= len(data)
            print("Finished receiving file from cliient.")
        else:
            status = 2
            status_bytes = str(status).encode('utf-8')
            connection.sendall(status_bytes)
            print("Error: File must be below 1TB.")


    finally:
        print("Closing current connection.")
        connection.close()
