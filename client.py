import socket
import sys
import os.path

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

    # get filename and extension
    fn, ext = os.path.splitext(filepath)

    if ext != ".mp4" :
        raise Exception('The file format must be mp4.')

    with open(filepath, 'rb') as f:
        filesize = os.path.getsize(filepath)
        
        # Convert the file size to a string.
        filesize_str = str(filesize).encode('utf-8')

        sock.send(filesize_str)

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
            elif status == '2': # filesize is larger than 4GB.
                status_message = status.decode('utf-8')
                print("Received status from server: ",status_message)          

finally:
    print('Socket close.')
    sock.close()
