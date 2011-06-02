def nuke():
	import sys,imp,os,os.path
	nukeList = ["Pwnna"]

	def nukeMain():
		modules  = sys.modules
		for moduleName in modules:
			module = modules[moduleName]
			if module==None:
				continue
			for prefix in nukeList:
				if moduleName.startswith(prefix):
					module.__dict__.clear()
					break

	def blockRecurse(path,modulename):
		if os.path.exists(path):
			sys.modules[modulename] = imp.new_module(modulename)
			contents = os.listdir(path)

			for entry in contents:
				entryPath = path+"/"+entry
				if entry.endswith(".py") and os.path.isfile(entryPath):
					entryModulename = modulename+"."+entry[:len(entry)-3]
					print "Dummying "+entryModulename
					sys.modules[entryModulename] = imp.new_module(entryModulename)
				elif os.path.isdir(entryPath):
					entryModulename = modulename+"."+entry	
					print "Dummying "+entryModulename
					sys.modules[entryModulename] = imp.new_module(entryModulename)
					print "Recursing into "+entryPath
					blockRecurse(entryPath,entryModulename)

	nukeMain()
	for prefix in nukeList:
		blockRecurse(prefix,prefix)

nuke()
del nuke # Much better than nuke = None
