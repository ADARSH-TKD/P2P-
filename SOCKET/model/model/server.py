import socket

s=socket.socket()
print('socket created')

s.bind(('localhost',9999))

s.listen(3)
print('waiting for the connection')

while True :
    c, add =s.accept()
    print("connection with",add)
    
    c.send(bytes('welcom to adarsh','utf-8'))
    
    c.close()