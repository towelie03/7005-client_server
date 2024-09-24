import os
import socket
import struct
import argparse

socket_path = "/tmp/socket"
line_len = 4096
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

def send_file(file_paths):
    try:
        s.connect(socket_path)

        try:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                s.sendall(struct.pack('!I', file_size))
                
                s.sendall(struct.pack('!I', len(file_name)))
                s.sendall(file_name.encode('utf-8'))

                with open(file_path, 'rb') as file:
                    while True:
                        chunk = file.read(line_len)
                        if not chunk:
                            break
                        s.sendall(chunk)
                
        except FileNotFoundError as fnf:
            print(f"file not found {fnf}")

        confirm_msg = s.recv(line_len)
        print(confirm_msg.decode())
    
    except socket.error as se:
        print(f"Socket error start server.py to bind the socket {se}")
    finally:
        s.close()

def main():
    parser = argparse.ArgumentParser(description='Send a files over a Unix domain socket.')
    parser.add_argument('file_paths', type=str, nargs='+', help='Path to the file to send.')

    args = parser.parse_args()

    send_file(args.file_paths)

if __name__ == "__main__":
    main()

