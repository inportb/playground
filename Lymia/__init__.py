def nuke():
	import sys,imp,os,os.path
	nukeList = ["Pwnna"]
	debug = False
	def nukeMain():
		modules  = sys.modules
		for moduleName in modules:
			module = modules[moduleName]
			if module==None:
				continue
			for prefix in nukeList:
				if moduleName.startswith(prefix):
					if debug: print "Nuking "+moduleName
					module.__dict__.clear()
					break

	def blockRecurse(path,modulename):
		if os.path.exists(path):
			if debug: print "Dummying "+modulename
			sys.modules[modulename] = imp.new_module(modulename)
			contents = os.listdir(path)

			for entry in contents:
				entryPath = path+"/"+entry
				if entry.endswith(".py") and os.path.isfile(entryPath):
					entryModulename = modulename+"."+entry[:len(entry)-3]
					if debug: print "Dummying "+entryModulename
					sys.modules[entryModulename] = imp.new_module(entryModulename)
				elif os.path.isdir(entryPath):
					if debug: print "Recursing into "+entryPath
					blockRecurse(entryPath,modulename+"."+entry)

	nukeMain()
	for prefix in nukeList:
		blockRecurse(prefix,prefix)

nuke()
del nuke # Much better than nuke = None
