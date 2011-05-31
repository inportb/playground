def nuke():
	import sys

	nukeList = ["Pwnna"]
	modules  = sys.modules
	for moduleName in modules:
		module = modules[moduleName]
		if module==None:
			continue
		for prefix in nukeList:
			if moduleName.startswith(prefix):
				module.__dict__.clear()
				break
nuke()
nuke = None
