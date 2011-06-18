try:
    from gevant.socket import *
except ImportError:
    from socket import *

from time import ctime
import os
# I just cannot not refactor this
class NetworkWrapper(object):
    def __init__(self, host, port, buffersize, conntype, isServer):
        self.address = (host, port)
        self.buffersize = buffersize
        self.socket = socket(AF_INET, conntype)
        if isServer:
            self.socket.bind(self.address)
            if conntype == SOCK_STREAM:
                self.socket.listen(5)

    def close(self):
        self.socket.close()

    def parseReturnData(self, data):
        raise NotImplementedError

    def __del__(self):
        self.socket.close()

class TCPServer(NetworkWrapper):
    def __init__(self, host="", port=12345, buffersize=1024):
        super(TCPServer, self).__init__(host, port, buffersize, SOCK_STREAM, True)
        self.clientsocket = None
        
    def run(self):
        running = True
        while running:
            print "Waiting for a connection..."
            self.clientsocket, address = self.socket.accept()
            print "Accepted from %s" % str(address)
            data = True
            while data and running:
                data = self.clientsocket.recv(self.buffersize)
                running = self.parseReturnData(data)
            self.clientsocket.close()
            self.clientsocket = None
            print "Destroyed connection from %s" % str(address)
        self.close()

    def returnMessage(self, message):
        if self.clientsocket:
            self.clientsocket.send(message)

class TCPClient(NetworkWrapper):
    def __init__(self, host, port=12345, buffersize=1024):
        super(TCPClient, self).__init__(host, port, buffersize, SOCK_STREAM, False)

    def connect(self):
        self.socket.connect(self.address)

    def sendData(self, data):
        self.socket.send(data)
        return self.socket.recv(self.buffersize)


class UDPServer(NetworkWrapper):
    def __init__(self, host="", port=12345, buffersize=1024):
        super(UDPServer, self).__init__(host, port, buffersize, SOCK_DGRAM, True)
        self.returnaddress = None
        
    def run(self):
        running = True
        while running:
            print "waiting for message..."
            data, self.returnaddress = self.socket.recvfrom(self.buffersize)
            running = self.parseReturnData(data)
        self.close()

    def returnMessage(self, message):
        if self.returnaddress:
            self.socket.sendto(message, self.returnaddress)
    

class UDPClient(NetworkWrapper):
    def __init__(self, host, port=12345, buffersize=1024):
        super(UDPClient, self).__init__(host, port, buffersize, SOCK_DGRAM, False)
        self.socket.settimeout(5)
        
    def sendData(self, data):
        self.socket.sendto(data, self.address)
        try:
            data, address = self.socket.recvfrom(self.buffersize)
        except timeout:
            return False, False
        return data, address   


# EXTRAS

class CommandServer(object):
    def __init__(self):
        self.commands = {}
        self.regcmd("invalid", self.onInvalidCommand)
        
    def regcmd(self, cmd, callback):
        self.commands[cmd.lower()] = callback

    def parseReturnData(self, data):
        data = data.strip().lower()
        data = data.split()
        if len(data) == 0:
            return True
        elif len(data) == 1:
            args = tuple()
        else:
            args = data[1:]
            
        cmd = data[0]
        
        callback = self.commands.get(cmd, None)
        if callback:
            return callback(args)
        else:
            return self.commands['invalid'](data)
            
    def onInvalidCommand(self, data):
        self.returnMessage("%s is not a valid command." % data)
        return True
        

class InfoServer(CommandServer):
    def __init__(self):
        CommandServer.__init__(self)
        self.regcmd("date", self.date)
        self.regcmd("os", self.os)
        self.regcmd("ls", self.ls)
        self.regcmd("shutdown", self.shutdown)
    
    def date(self, args):
        self.returnMessage(ctime())
        return True

    def os(self, args):
        self.returnMessage(os.name)
        return True

    def ls(self, args):
        args = list(args)
        if len(args) == 0:
            args.append(os.curdir)
                
        listings = "\n".join(os.listdir(args[0]))
        self.returnMessage(listings)
        return True

    def shutdown(self, data):
        return False
