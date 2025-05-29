import socket

c=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
c.connect(("10.147.20.135",8080))

payload= 'hey server'

try:
    while True:
        c.send(payload.encode('utf-8'))
        data= c.recv(1024)
        print(str(data))
        x = input(" want to send the more data  to the sever ")
        if x=='y' or x=='Y' :
            payload =input("Enter the payload : ")
        else:
            break
except KeyboardInterrupt:
    print("Exited by user")
c.close()
