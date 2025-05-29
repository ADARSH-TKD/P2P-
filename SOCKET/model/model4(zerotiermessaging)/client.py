# client.py
import socket

s = socket.socket()
s.connect(("10.147.20.135", 9999))  # Use the server's ZeroTier IP

s.send(b"Hello from client!")
data = s.recv(1024).decode()
print(f"Received from server: {data}")

s.close()
