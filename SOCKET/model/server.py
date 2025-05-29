# server.py
import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))  # Allow connections from any device on the network
server.listen(5)
print("Server running on 192.168.95.203:9999...")

while True:
    client, addr = server.accept()
    print(f"Connected by {addr}")
    data = client.recv(1024).decode()
    print(f"Received: {data}")
    client.send("Hello from server!".encode())
    client.close()