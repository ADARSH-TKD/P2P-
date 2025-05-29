# client.py
import socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.95.203', 9999))  # Use the server's local IP
client.send("Hello from client!".encode())
response = client.recv(1024).decode()
print(f"Server response: {response}")
client.close()