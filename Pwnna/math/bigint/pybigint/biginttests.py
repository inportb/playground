import unittest
from biginteger import BigInteger

class BigIntegerTest(unittest.TestCase):    
    tests = ((1, 1),
             (0, 0),
             (123, 999),
             (9979, 839),
             (3694, 58291),
             (38432, -94),
             (11, -234),
             (938, -9937),
             (-9485, 291),
             (-539, -2103),
             (-12, 304))
             
    def test_addition(self):
        for n1, n2 in self.tests:
            result = n1 + n2
            self.assertEqual(result, BigInteger(n1) + BigInteger(n2))
            self.assertEqual(result, BigInteger(n1) + n2)
            self.assertEqual(result, n1 + BigInteger(n2))
    
    def test_subtractions(self):
        for n1, n2 in self.tests:
            result = n1 - n2
            self.assertEqual(result, BigInteger(n1) - BigInteger(n2))
            self.assertEqual(result, BigInteger(n1) - n2)
            self.assertEqual(result, n1 - BigInteger(n2))
            
    def test_multiplications(self):
        for n1, n2 in self.tests:
            result = n1 * n2
            self.assertEqual(result, BigInteger(n1) * BigInteger(n2))
            self.assertEqual(result, BigInteger(n1) * n2)
            self.assertEqual(result, n1 * BigInteger(n2))
    
    def test_division(self):
        for n1, n2 in self.tests:
            result = n1 / n2
            self.assertEqual(result, BigInteger(n1) / BigInteger(n2))
            self.assertEqual(result, BigInteger(n1) / n2)
            self.assertEqual(result, n1 / BigInteger(n2))
