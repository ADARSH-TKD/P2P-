# client_send.py
import socket

s = socket.socket()
s.connect(("10.147.20.135", 5001))  # Replace with receiver's ZeroTier IP

with open("your_file.zip", "rb") as f:
    data = f.read(1024)
    while data:
        s.send(data)
        data = f.read(1024)

print("File sent successfully.")
s.close()
