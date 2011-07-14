#!/usr/bin/python
import socket as s
from threading import Thread
import logging
from chatcommons import *

class Client(object):
    class ClientThread(Thread): # Thread specifically written to handle incoming data
        def __init__(self, client):
            Thread.__init__(self)
            self.client = client

        def run(self):
            cl = self.client
            logging.info("Client '%s' thread has been started." % str(cl.addr))
            cl.running = True
            cc = cl.clientconn
            name = cc.recv(BUFSIZE)
            if not cl.validateName(name):
                cl.sendMessage("ERROR Name '%s' is not properly formatted or has been taken.")
                logging.warning("Client '%s' send an invalid name '%s'." % (cl.addr[0], name))
                cl.stop()
                return
            else:
                logging.info("Client '%s' has connected with name '%s'." % (cl.addr[0], name))
            
            self.name = name.strip().lower()
            self.server.clientConnected(self)

            # Main loop starts            
            while cl.running:
                data = cc.recv(BUFSIZE).strip()
                cmd, data = data.split(" ", 1)
                self.server.fireCommand(cmd, self, data)
                
            # Main loop ends
            
            logging.info("Client '%s' thread has been stopped." % str(cl.addr))
            
    
    def __init__(self, clientconn, addr, server):
        Threading.__init__(self)
        self.clientconn = clientconn
        self.addr = addr
        self.running = False
        self.name = False
        self.server = server

        self._thread = ClientThread(self)        

    def validateName(self, name):
        return " " not in name and name not in self.server.connectedClients and name != "server" and "|" not in name

    def start(self):
        self._thread.start()

    def join(self):
        self._thread.join()
        
    def __del__(self):
        self.stop()

    def stop(self, sendSignal=True):
        if sendSignal:
            self.sendMessage("DISCONNECT")
            
        self.running = False
        self.clientconn.close()
        self.server.clientDisconnected(self)

    def sendMessage(self, msg):
        if self.running:
            self.clientconn.send(msg)
        else:
            logging.warning("Client Connection already closed. Failed to send '%s'" % msg)

class ChatServer(object):
    class ServerThread(Thread):
        def __init__(self, server):
            Thread.__init__(self)
            self.server = server

        def run(self):
            logging.info("Server listening thread started...")
            server = self.server
            while server.running:
                logging.info("Waiting for a connection...")
                clientsocket, addr = server.serverSocket.accept()
                logging.info("Accepted connection from %s:%d" % addr)
                server.newClient(clientsocket, addr)
            logging.info("Server listening thread stopped.")

    def __init__(self, host, port):
        self.addr = (host, port)
        self.serverSocket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.running = False
        self.connectingClients = []
        self.connectedClients = {}
        self._serverThread = ServerThread(self)
        self.commands = {
                         "DISCONNECT" : self.disconnectClient,
                         "CHAT" : self.chat,
                         "LISTUSER" : self.listuser
                         }
                         
        self.serverCommands = {
                               "KICK" : self.kickClient,
                               "SHUTDOWN" : self.shutdownServer
                               "ANNOUNCE" : self.announce
                               }

    def listuser(self, client, data):
        users = "|".join(self.connectedClients.key())
        client.sendMessage("USERLIST %s" % users)

    def chat(self, client, data):
        client.sendMessage("CHAT %s %s" % (client.name, data))

    def disconnectClient(self, client, data):
        client.stop()

    def kickClient(self, data):
        data = data.strip()
        self.connectedClients[data].stop()
        self.connectedClients[data].join(3)

    def announce(self, message):
        self.broadcastMessage("CHAT SERVER %s" % message)

    def run(self):
        self.serverSocket.bind(self.addr)
        self.serverSocket.listen(5)
        self.running = True
        self._serverThread.start()
        try:
            while self.running:
                command, data = raw_input("> ").strip().lower().split(" ", 1)
                self.fireServerCommand(command, data)
        except KeyboardInterrupt:
            logging.warning("Keyboard Interrupted.")
            self.shutdownServer()
            
    def shutdownServer(self, data=None):
        print "Server is shutting down..."
        self.running = False
        
        for name in self.connectedClients:
            self.connectedClients[name].stop()
            self.connectedClients[name].join(3)

        for client in self.connectingClients:
            client.stop()
            client.join(3)

        self.serverSocket.close()
        print "Server shutdown complete."

    def broadcastMessage(self, message):
        for name in self.connectedClients:
            self.connectedClients[name].sendMessage(message)

    def newClient(self, clientsocket, address):
        cli = Client(clientsocket, addr, self)
        self.connectingClients.append(cli)
        cli.start()

    def clientConnected(self, client):
        self.connectingClients.remove(client)
        self.connectedClients[client.name] = client
        self.broadcastMessage("CONNECTED %s" % client.name)

    def clientDisconnected(self, client):
        del self.connectedClients[client.name]
        self.broadcastMessage("DISCONNECTED %s" % client.name)
        logging.info("Client %s has been signalled for disconnect." % str(client.addr))

    def registerCommand(self, cmd, callback):
        if cmd in self.commands: raise KeyError("The command '%s' is already registered." % cmd)
        self.commands[cmd] = callback

    def unregisterCommand(self, cmd):
        del self.commands[cmd]

    def fireCommand(self, command, client, data):
        self.commands[command].upper())(client, data)

    def fireServerCommand(self, command, data):
        self.serverCommands[command.upper()](data)
