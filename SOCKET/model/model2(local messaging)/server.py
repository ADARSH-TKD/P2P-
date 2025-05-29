import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 7634

s.bind((host, port))
s.listen(1)

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

conn.close()  # Close the connection after exiting the loop
