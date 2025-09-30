import socket
import os

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
        header = connection.recv(32)
        filesize_str = header.decode('utf-8')

        # convert string into int
        filesize = int(filesize_str)

        # check filesize and send status 1(smaller) or 2(larger)
        if filesize < pow(2,32):
            status = 1
            status_bytes = str(status).encode('utf-8')
            connection.sendall(status_bytes)

            #  recieve data in 1400 bytes
            with open(os.path.join(dpath,filesize_str),'wb+') as f:
                while filesize > 0:
                    data = connection.recv(1400)
        else:
            status = 2
            status_bytes = str(status).encode('utf-8')
            connection.sendall(status_bytes)
            # error_message = "Error: File must be below 4GB."


    finally:
        print("Closing current connection.")
        connection.close()
