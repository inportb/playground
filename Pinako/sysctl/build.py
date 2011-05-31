#!/usr/bin/env python

import re, pprint

breakpoint = '##### SYSCTL CONSTANTS #####'
sysctl_h = '/usr/include/linux/sysctl.h'

code = open('__init__.py').read().split(breakpoint,1)[0].rstrip()
f = open('__init__.py','w+')
print >>f,code
print >>f
print >>f,breakpoint
print >>f,'# from',sysctl_h
print >>f

const = {}
for line in open(sysctl_h,'r'):
	m = re.match(r'/\*([^\*]+)\*/',line)
	if m:
		print >>f,'#',m.group(1).strip()
		continue
	m = re.match(r'\s*([^=\s]+)\s*=\s*(\d+),?(?:\s*/\*([^\*]+)\*/)?',line)
	if m:
		m = m.groups()
		const[m[0]] = int(m[1])
		if m[2] is None:
			print >>f,'%s\t= %s'%(m[0],m[1])
		else:
			print >>f,'%s\t= %s\t# %s'%(m[0],m[1],m[2])
print >>f
print >>f,'__all__ =',pprint.pformat(['sysctl']+const.keys()).replace('\n ','\n\t')
