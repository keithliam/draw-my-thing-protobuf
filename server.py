import os
from socket import *
host = "192.168.43.101"
port = 13000
buf = 1024
addr = (host, port)
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.bind(addr)
print("Waiting to receive messages...")

def broadcast(sock, data):
  global addrList
  for addr in addrList:
    sock.sendto(data, addr)

addrList = []

(data, addr) = UDPSock.recvfrom(buf)
print(addr)
print(data)
host = addr

while True:
    (data, addr) = UDPSock.recvfrom(buf)
    print(addr)
    print(data)
    if addr != host:
      if addr not in addrList:
        addrList.append(addr)
        UDPSock.sendto(data, host)
    else:
      broadcast(data, host)
    print(data)
