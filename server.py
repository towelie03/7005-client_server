import os
import socket
import struct
import signal
import sys

socket_path = "/tmp/socket"
running = True
line_len = 4096
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

def signal_int(sig, frame):
    global running
    print("SIGINT received... Shutting down")
    running = False
    if os.path.exists(socket_path):
        os.remove(socket_path)
    sys.exit(0)

def ub_socket(socket_path):
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

def b_socket(socket_path):
    s.bind(socket_path)
    s.listen(1)
    socket_name = s.getsockname()
    print(f"Connected at {socket_name}")

def recv_file():
    try:
        while running:
            conn, client_addr = s.accept()
            try:
                while True:
                    file_size_data = conn.recv(4)
                    if not file_size_data:
                        break
                    file_size = struct.unpack('!I', file_size_data)[0]
                    print(f"File size: {file_size}")

                    file_name_size_data = conn.recv(4)
                    if not file_name_size_data:
                        break
                    file_name_size = struct.unpack('!I', file_name_size_data)[0]

                    file_name = conn.recv(file_name_size).decode('utf-8')
                    print(f"File name: {file_name}")

                    if not file_name or '\x00' in file_name:
                        raise ValueError("Invalid file name received.")

                    with open(file_name, 'wb') as file:
                        bytes_received = 0
                        while bytes_received < file_size:
                            chunk = conn.recv(min(file_size - bytes_received, line_len))
                            if not chunk:
                                break
                            file.write(chunk)
                            bytes_received += len(chunk)

                    print("\nFile contents:")
                    with open(file_name, 'r') as file:
                        file_contents = file.read()
                        print(f"{file_contents}")

                    print("File received\n")

            except Exception as e:
                print(f"error {e}")
                conn.close()

    except Exception as excep:
        print(f"error {excep}")
    finally:
        s.close()
        print("Server closed")


def main():
    signal.signal(signal.SIGINT,signal_int)
    print('Server is running... Press Ctrl+C to stop.')
    ub_socket(socket_path)
    b_socket(socket_path)
    recv_file()

if __name__ == "__main__":
    main()



