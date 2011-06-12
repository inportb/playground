def checkEgyptian(fn):
    with open(fn) as f:
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            if line.strip().startswith("{"):
                return False
        return True


    
