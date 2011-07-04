#!/usr/bin/env python
# basic infix calculator

import re
try:
	import readline
except ImportError:
	pass

class MathException(BaseException): pass

def shuntingyard(expr,precedence={'+':1,'-':1,'*':2,'/':2,'^':3}):
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

def postfix(expr,tutorial=False):
	stack = []
	for v in expr:
		if type(v) is float:
			stack.append(v)
			continue
		b = stack.pop()
		a = stack.pop()
		if v == '+':
			stack.append(a+b)
		elif v == '-':
			stack.append(a-b)
		elif v == '*':
			stack.append(a*b)
		elif v == '/':
			stack.append(a/b)
		elif v == '^':
			stack.append(a**b)
		else:
			raise MathException('invalid operator')
		if tutorial:
			print '\t|',a,v,b,'=',stack[-1]
	print stack

try:
	while True:
		expr = raw_input('MATH\t> ').strip()
		if len(expr) < 1:
			break
		if expr.endswith('?'):
			tutorial = True
			expr = expr[:-1]
		else:
			tutorial = False
		try:
			postfix(shuntingyard(re.findall(r'\d+|\W',re.sub(r'\s+','',expr))),tutorial)
		except MathException,ex:
			print ex[0]
except (EOFError,KeyboardInterrupt):
	print
