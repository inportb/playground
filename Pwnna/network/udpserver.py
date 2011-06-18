from simplenetwork import UDPServer, InfoServer

class UDPInfoServer(InfoServer, UDPServer):
    def __init__(self):
        InfoServer.__init__(self)
        UDPServer.__init__(self)
        

if __name__ == "__main__":
    server = UDPInfoServer()
    server.run()
