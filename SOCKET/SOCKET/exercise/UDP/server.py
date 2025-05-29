import socket

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind((' 10.147.20.135',8080))

while True:
    data,addr=s.recvfrom(4096)
    print(str(data))
    message=bytes("hello I an UDP server").encode('utf-8')
    s.sendto(message,addr)