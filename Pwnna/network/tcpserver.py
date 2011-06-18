from simplenetwork import TCPServer, InfoServer


class TCPInfoServer(InfoServer, TCPServer): # order does matter. OR else the TCPServer can't see the InfoServer's parseReturnData method.
    pass

if __name__ == "__main__":
    server = TCPInfoServer()
    server.run()
