import socket
import sys
import os
import stat

# Global variables
SOCKET_PATH = '/tmp/socket'
LINE_LEN = 4096

def check_socket_path():
    if os.path.exists(SOCKET_PATH):
        # Attempt to check if it's a socket file
        try:
            if stat.S_ISSOCK(os.stat(SOCKET_PATH).st_mode):
                os.remove(SOCKET_PATH)
                print(f"Removed existing socket file: {SOCKET_PATH}")
            else:
                print(f"Warning: '{SOCKET_PATH}' exists but is not a socket file.")
        except Exception as e:
            print(f"Error checking socket file: {e}")
    else:
        print(f"No existing socket file to remove at: {SOCKET_PATH}")

def setup_server_socket():
    try:        
        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(SOCKET_PATH)
        server_sock.listen(1)
        print(f"Server is listening on {SOCKET_PATH}")
        return server_sock
    except Exception as e:
        print(f"Error: Unable to create server socket: {e}")
        sys.exit(1)

def wait_for_connection(server_sock):
    try:
        conn, client_addr = server_sock.accept()
        return conn
    except Exception as e:
        print(f"Error: Unable to accept connection: {e}")
        return None

def process_request(requested_file):
    try:
        if os.path.isfile(requested_file):
            if not os.access(requested_file, os.R_OK):
                return f"Error: Permission denied for file '{requested_file}'"
            with open(requested_file, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            return f"Error: File '{requested_file}' not found."
    except Exception as e:
        return f"Error: Unable to read file '{requested_file}': {e}"

def send_reply(conn, reply):
    try:
        conn.sendall(reply.encode('utf-8'))
    except BrokenPipeError:
        print("Error: Client disconnected unexpectedly.")
    except Exception as e:
        print(f"Error: Unable to send response: {e}")

def main():
    server_sock = setup_server_socket()
    print("Ctrl+C to shutdown and exit")

    try:
        while True:
            conn = wait_for_connection(server_sock)
            if conn is None:
                continue

            try:
                file_req = conn.recv(LINE_LEN).decode('utf-8')
                if not file_req:
                    break
                
                print(f"Received file request: {file_req}")
                reply = process_request(file_req)
                send_reply(conn, reply)
            
            except Exception as e:
                print(f"Error handling request: {e}")
            finally:
                conn.close()

    except KeyboardInterrupt:
        print("\nShutting down and closing the connection")
    finally:
        server_sock.close()
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        print("Server socket removed")

if __name__ == "__main__":
    main()

