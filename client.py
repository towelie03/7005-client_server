import os
import socket
import struct
import argparse

# Hard-coded socket path
socket_path = "/tmp/socket"

def send_file(file_path):
    # Create a Unix domain socket
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:

        # Connect the socket to the path
        s.connect(socket_path)

        # Get the file name and size
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Send the file size
        s.sendall(struct.pack('!I', file_size))
        
        # Send the file name size and name
        s.sendall(struct.pack('!I', len(file_name)))
        s.sendall(file_name.encode('utf-8'))

        # Open the file and send its content
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                s.sendall(chunk)
        
        print("File sent successfully.")
        
        s.close()

def main():
    parser = argparse.ArgumentParser(description='Send a files over a Unix domain socket.')
    parser.add_argument('file_path', type=str, help='Path to the file to send.')

    args = parser.parse_args()

    send_file(args.file_path)

if __name__ == "__main__":
    main()

