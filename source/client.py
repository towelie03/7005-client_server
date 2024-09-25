import socket
import sys
import argparse

# Global variables
SOCKET_PATH = '/tmp/socket'
LINE_LEN = 4096

def parse_args():
    parser = argparse.ArgumentParser(description="Unix domain socket assignment 1")
    parser.add_argument('file_paths', nargs='+', help="Path of files to send")
    return parser.parse_args()  # Return the parsed arguments

def connect_to_server():
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCKET_PATH)
        return sock
    except Exception as e:
        print(f"Error: Unable to connect to server socket: {e}")
        sys.exit(1)

def send_file_request(sock, file_request):
    try:
        sock.sendall(file_request.encode('utf-8'))
    except Exception as e:
        print(f"Error: Unable to send request: {e}")
        sock.close()
        sys.exit(1)

def get_server_response(sock):
    try:
        data = ""
        while True:
            part = sock.recv(LINE_LEN).decode('utf-8')
            if not part:
                break
            data += part
        
        return data
    except Exception as e:
        print(f"Error: Unable to receive response: {e}")
        return None

def main():
    args = parse_args()  # Get the parsed arguments
    file_requests = args.file_paths  # Access the file_paths attribute
   
    for file_request in file_requests:
        sock = connect_to_server()
        send_file_request(sock, file_request.strip())
        
        data = get_server_response(sock)
        if data:
            print(f"Contents in {file_request}:\n{data}")
        sock.close()
    
if __name__ == "__main__":
    main()

