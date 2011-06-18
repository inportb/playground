from simplenetwork import TCPServer, InfoServer

class TCPInfoServer(InfoServer, TCPServer):
    def __init__(self):
        InfoServer.__init__(self)
        TCPServer.__init__(self)

if __name__ == "__main__":
    server = TCPInfoServer()
    server.run()
        
        
