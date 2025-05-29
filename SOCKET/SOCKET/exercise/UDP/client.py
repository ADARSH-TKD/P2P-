import socket
c = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

msg="hello udp server"
c.sendto(msg.encode('utf-8'),("10.147.20.135",8080))
data,addr=c.recvfrom(4096)
print("Server says: ")
print(str(data))
c.close()