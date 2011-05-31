import sys

def nuke():
	modules=sys.modules
	sys.modules=None
	for m in modules:
		if m==None:
			continue
		else:
			m.__dict__.clear()
nuke()
