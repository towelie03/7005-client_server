import os
import socket
import struct
import signal
import sys


socket_path = "/tmp/socket"
running = True

def signal_handler(sig, frame):
    global running
    print("\nSIGINT received, shutting down gracefully...")
    running = False

def recv_file(socket_path):
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:

        s.bind(socket_path)
        s.listen(1)

        print("Waiting for a connection...")
        conn, addr = s.accept()
        print("Connected")

        try:
            # Read the file size
            file_size = struct.unpack('!I', conn.recv(4))[0]
            print(f"File size: {file_size}")

            file_name_size = struct.unpack('!I', conn.recv(4))[0]
            file_name = conn.recv(file_name_size).decode('utf-8')
            print(f"File name: {file_name}")

            if not file_name or '\x00' in file_name:
                raise ValueError("Invalid file name received.")

            # Open the file and write the received data to it
            with open(file_name, 'wb') as file:
                bytes_received = 0
                while bytes_received < file_size:
                    chunk = conn.recv(min(file_size - bytes_received, 4096))
                    if not chunk:
                        break
                    file.write(chunk)
                    bytes_received += len(chunk)

            print("File received successfully.")

            print("\nFile contents:")
            with open(file_name, 'r') as file:
                file_contents = file.read()
                print(file_contents)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
            s.close()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    recv_file(socket_path)


if __name__ == "__main__":
    main()



