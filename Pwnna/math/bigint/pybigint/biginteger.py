class MathException(Exception): pass

class BigInteger(object):
    def __init__(self, number):
        self.number = str(number)
        if self.number[0] == "-":
            self.negative = True
            self.number = self.number[1:]
        else:
            self.negative = False
    
    def __mul__(self, other):
        if other == 1:
            return BigInteger(str(self))
        elif other == -1:
            i = BigInteger(str(self))
            i.negative = not i.negative
            return i
        elif other == 0:
            return BigInteger(0)
        
        result = []
        firstNum = list(self.number)
        secondNum = list(other.number)
        
        
        levels = []
        
        i = len(other.number)-1
        numOfZeros = 0
        
        carry = 0
        while i >= 0:
            levels.append([] + [0] * numOfZeros)
            for j in reversed(xrange(len(self.number)))::
                temp = str(int(self.number[j]) * int(other.number[i]) + carry)
                if len(temp) == 2:
                    carry = int(temp[0])
                    levels[numOfZeros].insert(0, int(temp[1]))
                else:
                    levels[numOfZeros].insert(0, int(temp[0]))
            i -= 1
            numberOfZeros += 1
            
        # Adding the levels together.
        
        
        
        
        for i in reversed(xrange(len(other.number))):
            levels.append([]+[0]*i)
            for j in reversed(xrange(len(self.number))):
                temp = int(self.number) * int(other.number)
                
    
    def __add__(self, other): # pass it the wrong type, BAM, WON'T WORK!
        raise NotImplementedError("THIS SHIZ DOES NOT WORK.")
        
        if type(other) == int:
            other = HugeNumber(other)
        
        result = []
        firstNum = list(self.number)
        
        secondNum = list(other.number)
        selfLen = len(self.number)
        otherLen = len(other.number)
        
        if selfLen > otherLen:
            secondNum = ([0] * (selfLen - otherLen)) + secondNum
        elif otherLen > selfLen:
            firstNum = ([0] * (otherLen- selfLen)) + firstNum
        
        carry = 0

        num1 = (firstNum, -1 if self.negative else 1)
        num2 = (secondNum, -1 if other.negative else 1)
        
        while firstNum and secondNum:
            num1digit = int(num1[0].pop()) * num1[1]
            num2digit = int(num2[0].pop()) * num2[1]
            temp = num1digit + num2digit
            if temp >= 10:
                temp -= 10
                carry = 1
            elif temp < 0:
                temp += 10
                carry = -1
            else:
                carry = 0
        
        
        
        
        s = []
        n1 = list(self.number)
        n2 = list(other.number)
        l1 = len(n1)
        l2 = len(n2)
        additional = 0
        if l1 > l2:
            smallernum = n2
            biggernum = n1
        else:
            smallernum = n1
            biggernum = n2
        
        def _add(n1, n2, additional):
            
            n1temp = int(n1.pop())
            n2temp = int(n2.pop())
            
            if self.negative:
                n1temp *= -1
            if other.negative:
                n2temp *= -1
            
            temp_num = n1temp + n2temp + additional
            
            if temp_num < 0:
                temp_num = str(10 + temp_num)
                s.insert(0, temp_num[-1])
                return -1
            else:
                temp_num = str(temp_num)
                if len(temp_num) == 2:
                    i = int(temp_num[0])
                else:
                    i = 0
                s.insert(0, temp_num[-1])
                return i
        
        while smallernum:
            additional = _add(smallernum, biggernum, additional)
        
        n2 = [0] * len(biggernum)
        
        while biggernum:
            additional = _add(biggernum, n2, additional)
        
        return BigInteger("".join(s))

        
    
    def __str__(self):
        if self.negative:
            return "-" + self.number
        else:
            return self.number
    
    def __repr__(self):
        return self.__str__()



def testing(n1, n2):
    expected = n1 + n2
    actual = BigInteger(n1) + BigInteger(n2)
    if expected != int(actual.number):
        print n1, "+", n2, "failed. Expected:", expected, "Actual:", actual.number
    else:
        print "Passed. "


testing(123, 343)
testing(6839, 12)
testing(928481038192, 99999)
testing(4938294, 607943848739)
testing(-21, -23)
testing(21, -23)
testing(21, -21)
testing(-21, 23)
testing(-123, 2)
testing(123, -2)
