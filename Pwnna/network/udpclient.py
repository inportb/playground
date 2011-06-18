from simplenetwork import UDPClient

if __name__ == "__main__":
    addr = raw_input("Enter server address: ")
    client = UDPClient(addr)
    while True:
        data = raw_input(">> ")
        if not data:
            print "exitting..."
            break
        data, address = client.sendData(data)
        if not data:
            print "exitting..."
            break
        print data
    client.close()
