import socket
import sys
import os.path
import json

def protocol_header(json_length, mediatype_length, payload_length):
    return json_length.to_bytes(2,'big') + mediatype_length.to_bytes(1,'big') + payload_length.to_bytes(5,'big')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = input("Type in the server's address to connect to: ")
server_port = 9001

print('connecting to {}.'.format(server_address,server_port))

try:
    sock.connect((server_address,server_port))
except socket.error as err:
    print(err)
    sys.exit(1)

try:
    filepath = input('Type in a file to upload: ')
    action = input('Type in action (compress, resize, aspect, toaudio, gif): ')
    
    # get filename and extension
    filepath_with_ext = os.path.basename(filepath)
    fn, ext = os.path.splitext(filepath_with_ext)

    if action == 'compress':
        d = {
            'action': action,
            'filename': fn,
        }
    elif action == 'resize':
        width , height = map(int, input('Type in width and height (e.g., 1280 720): ').split())
        d = {
            'action': action,
            'filename': fn,
            'width': width,
            'height': height
        }
    elif action == 'aspect':
        aspect_ratio = input('Type in aspect ratio (e.g., 16:9):')
        d = {
            'action': action,
            'filename': fn,
            'aspect_ratio': aspect_ratio
        }
    elif action == 'toaudio':
        d = {
            'action': action,
            'filename': fn,
        }
    elif action == 'gif':
        starttime , duration = map(int, input('Type in start time and duration (e.g., 5 10): ').split())
        d = {
            'action': action,
            'filename': fn,
            'start_time': starttime,
            'duration': duration
        }   

    json_data = json.dumps(d).encode('utf-8')
    
    with open(filepath, 'rb') as f:
        filesize = os.path.getsize(filepath)

        if filesize >= pow(2,40):
            raise Exception("File size must be below 1TB.")
        
        ext_bits = ext.encode('utf-8')

        header = protocol_header(len(json_data), len(ext_bits), filesize)

        sock.send(header)

        sock.send(json_data)

        sock.send(ext_bits)

        data = f.read(1400)
        while data:
            sock.send(data)
            data = f.read(1400)
    print("File upload completed.")

    header = sock.recv(8)
    json_length = int.from_bytes(header[:2],'big')
    mediatype_length = int.from_bytes(header[2:3],'big')
    payload_length = int.from_bytes(header[3:8],'big')

    json_data = sock.recv(json_length).decode('utf-8')
    mediatype = sock.recv(mediatype_length).decode('utf-8')

    json_dist = json.loads(json_data)

    full_filename = json_dist['filename'] + mediatype

    byte_remaining = payload_length
    with open(full_filename,'wb+') as f:
        print(f"Start receiving file from server: {full_filename}")
        while byte_remaining > 0:
            byte_min = min(1400, byte_remaining)
            data = sock.recv(byte_min)
            f.write(data)
            byte_remaining -= len(data)
    print("Finished receiving file from server.")

finally:
    print('Socket close.')
    sock.close()
