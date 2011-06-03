"""Trapeze

Utility functions for roughly finding areas under graphical curves.

"""

from types import LongType, FloatType, MethodType, IntType

def integrate(b, a, y, ords):
	"""Trapezium/trapezoidal integration

	Estimates Integral(a, b, y, dx) by dividing the area into a set amount
	of trapezia/trapezoids and returning the sum of their areas.

	Parameters
	b    -- The x-coordinate at which the region of area ends.
	a    -- The x-coordinate at which the region of area starts.
	y    -- The function of the curved region.
	ords -- The number of ordinate (lines) used to make trapezia/trapezoids.

	"""
	
	# Real programmers use type checks!
	assert type(b) is IntType or type(b) is LongType, "b is not an integer number!"
	assert type(a) is IntType or type(a) is LongType, "a is not an integer number!"
	assert type(y) is MethodType, "y is not a function or lambda!"
	assert type(ords) is IntType or type(ords) is LongType, "ords is not an integer number!"

	# There is nothing immediatly wrong with these but they may lead to oddities.
	assert b > a, "Start (a) cannot have a larger value than the end (b)!"
	assert ords > 1, "There must be at least 2 ordinates!"
	
	# Make sure this is a usable function for our purposes
	# b is used because any constant used may not be in the valid
	# range for the function provided.
	assert type(y(b)) is IntType or type(y(b)) is FloatType or type(y(b)) is LongType, "y is not a usable function (it doesn't return a number)!"
	
	n = ords - 1 # number of 'strips'
	h = (b - a) / float(n) # work out the height of every trapezium
	
	# for every ordinate, calculate the y-distance between the x axis the point,
	# and append it's value to the list yn
	# also, delicious generators!
	yn = [y(a + (h * i)) for i in xrange(n + 1)] # call passed function with the x-coordinate to retrive y-coordinate, and append it

	# the total area
	total = 0.5 * h * (yn.pop(0) + yn.pop() + 2 * sum(yn))

	return total

if __name__ == "__main__":
	print integrate_trapeze(4, 0, lambda x: 16 - 2**x, 2000000)

