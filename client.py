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
    filepath = input('Type in a file to upload:')
    action = input('Type in action : ')

    # get filename and extension
    fn, ext = os.path.splitext(filepath)

    d = {
        'action': action,
        'filename': os.path.basename(filepath),}
    json_data = json.dumps(d).encode('utf-8')
    
    with open(filepath, 'rb') as f:
        filesize = os.path.getsize(filepath)
        
        # Convert the filesize and extension to a string.
        filesize_str = filesize.encode('utf-8')
        ext_bits = ext.encode('utf-8')

        header = protocol_header(len(json_data), len(ext_bits), len(filesize_str))

        sock.send(header)

        while True:
            status_bytes = sock.recv(16)
            status = status_bytes.decode('utf-8')
            if status == '1': # filesize is not error.
                # Send data divided into 1400 byte packets
                data = f.read(1400)
                while data:
                    print("sending...")
                    sock.send(data)
                    data = f.read(1400)
                sock.close()
            elif status == '2': # filesize is larger than 1TB.
                status_message = status.decode('utf-8')
                print("Received status from server: ",status_message)          

finally:
    print('Socket close.')
    sock.close()
