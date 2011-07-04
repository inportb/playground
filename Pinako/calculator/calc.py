#!/usr/bin/env python
# basic infix calculator

import re

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
		elif v == '+':
			if tutorial:
				a = stack.pop()
				b = stack.pop()
				stack.append(a+b)
				print '\t|',b,'+',a,'=',a+b
			else:
				stack.append(stack.pop()+stack.pop())
		elif v == '-':
			if tutorial:
				a = stack.pop()
				b = stack.pop()
				stack.append(-a+b)
				print '\t|',b,'-',a,'=',b-a
			else:
				stack.append(-stack.pop()+stack.pop())
		elif v == '*':
			if tutorial:
				a = stack.pop()
				b = stack.pop()
				stack.append(a*b)
				print '\t|',b,'*',a,'=',a*b
			else:
				stack.append(stack.pop()*stack.pop())
		elif v == '/':
			if tutorial:
				a = stack.pop()
				b = stack.pop()
				stack.append(1.0/a*b)
				print '\t|',b,'/',a,'=',b/a
			else:
				stack.append(1.0/stack.pop()*stack.pop())
		elif v == '^':
			a = stack.pop()
			b = stack.pop()
			stack.append(b**a)
			if tutorial:
				print '\t|',b,'^',a,'=',b**a
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
