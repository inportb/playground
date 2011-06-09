evalStrBase = """
class FunctionWrapper:
	def __init__(self,oldfunc,newfunc,prob):
		rng = LCG()

		self.:OLDFUNC: = oldfunc
		self.:NEWFUNC: = newfunc
		self.:PROB:    = lambda:prob
		self.:RNG:     = rng.rand
	def __call__(self,*args):
		if self.:RNG:(100)<self.:PROB:():
			return self.:NEWFUNC:(self.:OLDFUNC:,*args)
		else:
			return self.:OLDFUNC:(*args)

evalClass = FunctionWrapper
"""

def init():
	import sys, time

	class LCG:
		def __init__(self):
			self.seed=int(time.clock()*10000)
		def rand(self,max):
			self.seed=(self.seed*25214903917+11)%0xFFFFFFFFFFFF
			return self.seed%max
		def choice(self, lst):
			self.seed=(self.seed*25214903917+11)%0xFFFFFFFFFFFF
			return lst[self.seed%len(lst)]
		def randstr(self, length, chars):
			return "".join(self.choice(chars) for x in range(length))
	def makeClass():
		randomchrs = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
		evalStr   = evalStrBase

		rng = LCG()
		evalStr = evalStr.replace(":OLDFUNC:",rng.randstr(16,randomchrs))
		evalStr = evalStr.replace(":NEWFUNC:",rng.randstr(16,randomchrs))
		evalStr = evalStr.replace(":PROB:"   ,rng.randstr(16,randomchrs))
		evalStr = evalStr.replace(":RNG:"    ,rng.randstr(16,randomchrs))

		tdict = {"LCG":LCG}
		exec evalStr in tdict

		return tdict["evalClass"]

	mungeList = {
		"__builtin__": {
			"str": (lambda old,x:old(x).encode("base64"),30)
		}
	}

	for x in mungeList.keys():
		module = None
		try:
			module = sys.modules[x]
		except KeyError:
			continue
		if module==None:
			continue

		subList = mungeList[x]
		for y in subList.keys():
			cls = makeClass()
			module.__dict__[y] = cls(module.__dict__[y],subList[y][0],subList[y][1])

init()
del init
del evalStrBase
