import socket
import sys
try:
    s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
except socket.error as err:
    print("faile to create a socket ")
    print("reason"+str(err))
    sys.exit()
print("socket is created ")

target_host=input("enter the traget host name to connect : ")
target_port=input("enter the target port : ")

try:
    s.connect((target_host, int(target_port)))
    print("socket is connected to :"+target_host+target_port)
    s.shutdown(2)

except socket.error as err:
    print("Failed to connect to :"+target_port+target_host)
    print("reason:"+str(err))
    sys.exit()

