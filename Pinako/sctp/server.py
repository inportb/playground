import socket

IPPROTO_SCTP	= 132

SCTP_IP		= '127.0.0.1'
SCTP_PORT	= 5005

sock = socket.socket(socket.AF_INET,socket.SOCK_SEQPACKET,IPPROTO_SCTP)
sock.bind((SCTP_IP,SCTP_PORT))
sock.listen(256)

while True:
	data,(ip,port) = sock.recvfrom(1024)
	print '[%s:%d] %s'%(ip,port,data)
	sock.sendto(' '.join((data,)*128),(ip,port))
