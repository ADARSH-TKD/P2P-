import socket
import os
import struct

def receive_file(s, save_directory="downloads"):
    """Receive a file from the server"""
    try:
        # Create downloads directory if it doesn't exist
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        # Receive file size
        file_size_bytes = s.recv(8)
        if len(file_size_bytes) != 8:
            print("Error receiving file size")
            return False
            
        file_size = struct.unpack('!Q', file_size_bytes)[0]
        
        if file_size == 0:
            print("Server reported file error or file not found")
            return False
            
        print(f"Receiving file of size: {file_size} bytes")
        
        # Receive file name length
        file_name_len_bytes = s.recv(4)
        file_name_len = struct.unpack('!I', file_name_len_bytes)[0]
        
        # Receive file name
        file_name_bytes = s.recv(file_name_len)
        file_name = file_name_bytes.decode('utf-8')
        
        # Full path for saving
        file_path = os.path.join(save_directory, file_name)
        print(f"Saving as: {file_path}")
        
        # Receive file data
        with open(file_path, 'wb') as f:
            bytes_received = 0
            while bytes_received < file_size:
                chunk_size = min(4096, file_size - bytes_received)
                chunk = s.recv(chunk_size)
                if not chunk:
                    print("Connection lost during file transfer")
                    return False
                    
                f.write(chunk)
                bytes_received += len(chunk)
                
                # Show progress
                progress = (bytes_received / file_size) * 100
                print(f"Progress: {progress:.1f}% ({bytes_received}/{file_size} bytes)", end='\r')
        
        print(f"\nFile received successfully: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error receiving file: {e}")
        return False

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Replace with server's IP address
    host = '192.168.31.43'  # Change this to server's IP for different computers
    port = 8080

    try:
        s.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        while True:
            print("\nWaiting for server...")
            
            # Receive message type
            msg_type = s.recv(7)  # MESSAGE, FILE   , or QUIT   
            if not msg_type:
                print("Server disconnected.")
                break
            
            msg_type = msg_type.decode('utf-8').strip()
            
            if msg_type == 'MESSAGE':
                # Receive regular message
                msg_len_bytes = s.recv(4)
                msg_len = struct.unpack('!I', msg_len_bytes)[0]
                message = s.recv(msg_len).decode('utf-8')
                print(f"Message from server: {message}")
                
            elif msg_type == 'FILE':
                # Receive file
                print("Server is sending a file...")
                if receive_file(s):
                    print("File transfer completed successfully!")
                else:
                    print("File transfer failed!")
                    
            elif msg_type == 'QUIT':
                print("Server is closing connection.")
                break
            
            else:
                print(f"Unknown message type: {msg_type}")
            
            # Send response to server
            response = input("Send response to server: ")
            s.send(response.encode('utf-8'))

    except ConnectionRefusedError:
        print(f"Could not connect to server at {host}:{port}")
        print("Make sure the server is running and the IP address is correct.")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        s.close()
        print("Client closed.")

if __name__ == "__main__":
    main()