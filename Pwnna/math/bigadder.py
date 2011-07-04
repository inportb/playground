
class MathException(Exception): pass

def testing(n1, n2):
    expected = n1 + n2
    actual = int(bigIntAdder(str(n1), str(n2)))
    if expected != actual:
        raise MathException("lulz algorithm failed: %d + %d != %d == $d" % (n1, n2, actual, expected))
    else:
        print "Passed."


def bigIntAdder(n1, n2):
    s = []
    n1 = list(n1)
    n2 = list(n2)
    l1 = len(n1)
    l2 = len(n2)
    additional = 0
    if l1 > l2:
        smallernum = n2
        biggernum = n1
    else:
        smallernum = n1
        biggernum = n2
    
    def _add(n1, n2):
        temp_num = int(n1.pop()) + int(n2.pop()) + additional
        temp_num = str(temp_num)
        if len(temp_num) == 2:
            i = int(temp_num[0])
        else:
            i = 0
        s.insert(0, temp_num[-1])
        return i
    
    while smallernum:
        additional = _add(smallernum, biggernum)
    
    n2 = [0] * len(biggernum)
    
    while biggernum:
        additional = _add(biggernum, n2)
    
    return "".join(s)

testing(123, 343)
testing(6839, 12)
testing(928481038192, 99999)
testing(4938294, 607943848739)
