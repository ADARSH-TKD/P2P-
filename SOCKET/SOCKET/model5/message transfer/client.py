import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Replace with the server's IP address
#host = '192.168.31.43'  # Example IP - use server's actual IP
#port = 7634

s.connect(('192.168.31.43', 8080))

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