# server.py
import socket

s = socket.socket()
s.bind(("10.147.20.135", 9999))  # Use this system's ZeroTier IP
s.listen(1)
print("Server is listening...")

conn, addr = s.accept()
print(f"Connected with {addr}")

data = conn.recv(1024).decode()
print(f"Received from client: {data}")

conn.send(b"Hello from server!")
conn.close()
s.close()
