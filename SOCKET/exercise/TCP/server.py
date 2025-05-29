import socket

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('10.147.20.135',8080))
s.listen(5)

while True:
    print("Server waiting for connection")
    c,addr=s.accept()
    print("client connectes from ",addr)
    while True:
        data =c.recv(1024)
        if not data or data.decode("utf-8")=="END":
            break
        print("recieved from client client :%s" % data.decode("utf-8"))
        try:
            c.send(bytes('heyy client','utf-8'))
        except:
            print("Exited but the user ")
    c.close()
s.close()

