from simplenetwork import UDPServer, InfoServer

class UDPInfoServer(InfoServer, UDPServer):
    pass
        

if __name__ == "__main__":
    server = UDPInfoServer()
    server.run()
