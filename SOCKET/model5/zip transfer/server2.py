import socket
import os
import struct


def send_file(conn, file_path):
    """Send a file to the connected client"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist!")
            # Send error message
            conn.send(struct.pack('!Q', 0))  # Send 0 as file size to indicate error
            return False

        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"Sending file: {file_path} ({file_size} bytes)")

        # Send file size first
        conn.send(struct.pack('!Q', file_size))

        # Send file name
        file_name = os.path.basename(file_path)
        file_name_bytes = file_name.encode('utf-8')
        conn.send(struct.pack('!I', len(file_name_bytes)))
        conn.send(file_name_bytes)

        # Send file data in chunks
        with open(file_path, 'rb') as f:
            bytes_sent = 0
            while bytes_sent < file_size:
                chunk = f.read(4096)  # Read 4KB chunks
                if not chunk:
                    break
                conn.send(chunk)
                bytes_sent += len(chunk)

                # Show progress
                progress = (bytes_sent / file_size) * 100
                print(f"Progress: {progress:.1f}% ({bytes_sent}/{file_size} bytes)", end='\r')

        print(f"\nFile sent successfully!")
        return True

    except Exception as e:
        print(f"Error sending file: {e}")
        return False


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = '192.168.31.43'
    port = 8080

    try:
        s.bind((host, port))
        s.listen(1)
        print(f"Server listening on port {port}")

        conn, addr = s.accept()
        print(f"Connection established with {addr}")

        while True:
            print("\nOptions:")
            print("1. Send a message")
            print("2. Send a file")
            print("3. Quit")

            choice = input("Choose an option (1/2/3): ")

            if choice == '1':
                # Send regular message
                message = input("Enter message to send: ")
                conn.send(b'MESSAGE')  # Send message type
                conn.send(struct.pack('!I', len(message)))
                conn.send(message.encode('utf-8'))

            elif choice == '2':
                # Send file
                file_path = input("Enter full path to the file: ")
                conn.send(b'FILE   ')  # Send file type (padded to 7 bytes)
                send_file(conn, file_path)

            elif choice == '3':
                conn.send(b'QUIT   ')
                break

            else:
                print("Invalid choice!")
                continue

            # Wait for client response
            print("Waiting for client response...")
            try:
                response = conn.recv(1024)
                if response:
                    print(f"Client response: {response.decode('utf-8')}")
                else:
                    print("Client disconnected.")
                    break
            except:
                print("Error receiving response from client.")
                break

    except OSError as e:
        print(f"Server error: {e}")
    finally:
        s.close()
        print("Server closed.")


if __name__ == "__main__":
    main()