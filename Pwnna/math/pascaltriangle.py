
# Asked by a math teacher? Good enough reason to make this?

def pascal(n):
    n = int(n)
    if n == 1:
        return [[1]]
    else:
        result = pascal(n-1)
        last = result[-1]
        result.append([(a + b) for a,b in zip([0]+last, last+[0])])
        return result

def printpascal(n, fillspace=80):
    triangle_in_a_list = pascal(n)
    for line in triangle_in_a_list:
        for i in range(len(line)):
            line[i] = str(line[i])
        print " ".join(line).center(fillspace)

if __name__ == "__main__":
    while True:
        try:
            n = raw_input("Enter n (0-999, x to quit): ")
            if n.lower() == "x":
                break
            n = int(n) + 1
            if n >= 999:
                raise ValueError
        except ValueError:
            print "not a valid number!"
            continue
        else:
            printpascal(n)
