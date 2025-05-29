import socket
from _thread import *
s=socket.socket(socket.AF_INET,socket.)

host="10.147.20.135"
port=8080
ThreadCount=0

try:
    s.bind((host,port))
except socket.error as err:
    print(str(err))
print('waiting for connection...')
s.listen(5)

def 