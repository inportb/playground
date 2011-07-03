import socket
import threading
import Queue
import logging

tq = Queue.Queue()

class ChatClientReceive(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind("", 20000)
        self.socket.listen(5)
        self.commands = {"MSG": self.output}
        self.connected = False
    
    def run(self):
        logging.info("ChatClientReceive Started.")
        while self.connected:
            clientsocket, address = self.socket.accept()
            while True:
                data = clientsocket.recv(1024)
                data = data.split(":")
                if len(data) == 0:
                    break
                else:
                    self.commands[data[0].upper()](data)
            clientsocket.close()
        self.socket.close()
        logging.info("ChatClientReceive Ended.")
        tq.get()
        tq.task_done()
        
    def output(self, msg):
        print msg[1] + ": " + msg[2]
                

class ChatClient(object):
    def __init__(self, host):
        self.address = (host, 20001)
        self.buffersize = 1024
        self.sendsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvsocket = ChatClientReceive()
        self.sessionid = None
        tq.put(self)
    
    def fetchMessage(self):
        return self.messages.pop(0)
    
    def _sendData(self, data):
        self.sendsocket.send(data)
        return self.sendsocket.recv(self.buffersize).strip()
    
    def connect(self, nickname):
        self.sendsocket.connect(self.address)
        
        self.recvsocket.connected = True
        self.recvsocket.start()
        
        data = self._sendData("NICK:%s" % nickname)
        data = data.split(":")
        self.sessionid = data[0]
        return data[1]

    def disconnect(self):
        self._sendData("DISCONNECT")
        self.recvsocket.connected = False
        self.sendsocket.close()
        
    def getusers(self):
        return eval(self._sendData("LISTUSERS"))
    
    def sendChat(self, target, message):
        self._sendData("MSG:%s:%s" % (target, message))
        
class ConsoleChatClient(object):
    def __init__(self, nick, host):
        self.nick = nick
        self.client = ChatClient(host)
        print self.client.connect(nick)
        print "Your session ID is: %s" % self.client.sessionid
        self.target = None
    
    def getusers(self, data):
        users = self.client.getusers()
        print "SID : NICK"
        for sid in users:
            print "%s : %s" % (sid, users[sid])
    
    def disconnect(self, data):
        self.client.disconnect()
    
    def setTarget(self, data):
        self.target = data[1]
    
    def run(self):
        
        cmdmap = {"LISTUSER" : self.getusers,
                  "DISCONNECT" : self.disconnect,
                  "TALKTO" : self.setTarget}
        self.getusers(None)    
        while True:
            cmd = raw_input(">> ").strip().split(" ", 1)
            cmdmap[cmd[0]](cmd)
            
if __name__ == "__main__":
    cli = ConsoleChatClient(raw_input("Nick: ").strip(), raw_input("Host: ").strip())
    cli.run()
    tq.join()
            
            
