# server_receive.py
import socket

s = socket.socket()
s.bind(("0.0.0.0", 5001))  # Bind to all interfaces on port 5001
s.listen(1)
print("Waiting for connection...")

conn, addr = s.accept()
print(f"Connected by {addr}")

with open("received_file.zip", "wb") as f:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        f.write(data)

print("File received successfully.")
conn.close()
