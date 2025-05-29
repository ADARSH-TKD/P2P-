import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Option 1: Bind to all interfaces (recommended)
#host = '192.168.31.43'  # This allows connections from any IP
# Option 2: Use specific IP address
# host = '192.168.1.100'  # Replace with server's actual IP

#port = 7634

s.bind(('192.168.31.43', 8080))
s.listen(3)

conn, addr = s.accept()
print("Connection with", addr)

while True:
    messg = input("Send message to client: ")
    conn.send(messg.encode())

    print("Waiting for the response...")
    c_messg = conn.recv(1024)

    if not c_messg:
        print("Client disconnected.")
        break

    print("Message from client:", c_messg.decode())

conn.close()