def nuke():
	import sys,imp

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

	for prefix in nukeList:
		sys.modules[prefix] = imp.new_module(prefix)
	
nuke()
del nuke # Much better than nuke = None
