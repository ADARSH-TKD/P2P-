import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 7634

s.connect((host, port))

while True:
    print("Waiting for the response...")
    s_messg = s.recv(1024)

    if not s_messg:
        print("Server disconnected.")
        break

    print("Message from server:", s_messg.decode())

    c_messg = input("Send message to server: ")
    s.send(c_messg.encode())

s.close()
