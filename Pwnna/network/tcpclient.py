from simplenetwork import TCPClient

if __name__ == "__main__":
    client = TCPClient(raw_input("Enter server address: "))
    client.connect()
    while True:
        data = raw_input(">> ")
        if not data:
            print "exitting..."
            break
        data = client.sendData(data)
        if not data:
            print "exitting..."
            break
        print data
    client.close()
