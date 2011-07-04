#!/usr/bin/env python
# basic infix calculator

class MathException(BaseException): pass

def shuntingyard(expr,precedence={'+':1,'-':1,'*':2,'/':2}):
	stack = []
	for v in expr:
		try:
			yield float(v)
		except ValueError:
			if v == '(':
				stack.append(v)
			elif v == ')':
				try:
					while stack[-1] != '(':
						yield stack.pop()
					else:
						stack.pop()
						continue
					raise MathException('parenthesis mismatch')
				except IndexError:
					pass
			else:
				try:
					while precedence[v] <= precedence[stack[-1]]:
						yield stack.pop()
				except IndexError:
					pass
				except KeyError:
					if v not in precedence:
						raise MathException('invalid operator '+v)
				stack.append(v)
	for op in reversed(stack):
		if op in '()':
			raise MathException('parenthesis mismatch')
		yield op

try:
	while True:
		expr = raw_input('MATH> ').strip()
		if len(expr) < 1:
			break
		try:
			stack = []
			for v in shuntingyard(expr.split()):
				if type(v) is float:
					stack.append(v)
				elif v == '+':
					stack.append(stack.pop()+stack.pop())
				elif v == '-':
					stack.append(-stack.pop()+stack.pop())
				elif v == '*':
					stack.append(stack.pop()*stack.pop())
				elif v == '/':
					stack.append(1.0/stack.pop()*stack.pop())
			print stack
		except MathException,ex:
			print ex[0]
except (EOFError,KeyboardInterrupt):
	print
