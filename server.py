import os
import socket
import struct
import signal
import sys


socket_path = "/tmp/socket"
running = True

def signal_int(sig, frame):
    global running
    print("SIGINT received... Shutting down")
    if os.path.exists(socket_path):
        os.remove(socket_path)
    sys.exit(0)


def ubound(socket_path):
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise


def recv_file(socket_path):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(socket_path)
        s.listen(1)
        socket_name = s.getsockname()

        print(f"Connected at {socket_name}")

        try:
            while running:
                conn, addr = s.accept()
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

        except Exception as excep:
            print(f"An error occurred: {excep}")
        finally:
            s.close()
            print("Server closed")

def main():

    signal.signal(signal.SIGINT,signal_int)

    print('Server is running... Press Ctrl+C to stop.')

    ubound(socket_path)
    recv_file(socket_path)


if __name__ == "__main__":
    main()



