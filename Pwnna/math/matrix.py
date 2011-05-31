# Meh. I got bored in Math.

class Matrix(object):
    def __init__(self, matrix, numcolumn=-1):
        self.rows = matrix
        
        if numcolumn == -1:
            numcolumn = len(matrix[0])
            
        for row in matrix:
            if len(row) != numcolumn:
                raise TypeError("Columns must be in the same length.")
            
        self.columns = []
        for i in range(numcolumn):
            self.columns.append([])
            
        for row in matrix:
            for i in range(numcolumn):
                self.columns[i].append(row[i])
    
    def prettify(self, decimal=1):
        txt = ""
        decimal = str(decimal)
        formatstr = "%."+decimal+"f  "
        for row in self.rows:
            for num in row:
                txt += formatstr % num
            txt += "\n"
        return txt

    def _addsubtractcheck(self, other):
        if len(self.rows) != len(other.rows):
            raise ValueError("The number of rows doesn't match!")

        if len(self.columns) != len(other.columns):
            raise ValueError("The number of columns doesn't match!")

    def _doaddsubtract(self, other, add=True):
        self._addsubtractcheck(other)
        newMatrix = []
        for i in range(len(self.rows)):
            newMatrix.append([])
            for j in range(len(self.columns)):
                if add:
                    newMatrix[i].append(self.rows[i][j] + other.rows[i][j])
                else:
                    newMatrix[i].append(self.rows[i][j] - other.rows[i][j])
        return Matrix(newMatrix)

    def transform(self):
        return Matrix(self.columns)
    
    def __add__(self, other):
        return self._doaddsubtract(other)
        

    def __sub__(self, other):
        return self._doaddsubtract(other, False)

    def __mul__(self, other):
        newMatrix = []
        if type(other) == int:
            for i in range(len(self.rows)):
                newMatrix.append([])
                for j in range(len(self.columns)):
                    newMatrix[i].append(self.rows[i][j] * other)

            return Matrix(newMatrix)
            
        if len(self.columns) != len(other.rows):
            raise ValueError("The number of the columns in the first matrix doesn't match the number of the rows in the second matrix.")

        for rownum in range(len(self.rows)):
            newMatrix.append([])
            for colnum in range(len(other.columns)):
                value = 0
                for i in range(len(self.rows[rownum])):
                    value += self.rows[rownum][i] * other.columns[colnum][i]
                newMatrix[rownum].append(value)
                
        return Matrix(newMatrix)

if __name__ == "__main__":
    
    m2 = Matrix(((1,-6), (3,2)))
    print m1.prettify()
    print "multiple"
    print
    print m2.prettify()
    print "equals"
    print
    m3 = m1 * m2
    print m3.prettify()
