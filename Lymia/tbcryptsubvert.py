def run():
	import sys, StringIO, traceback

	oldstdout = sys.stdout
	oldstderr = sys.stderr
	sio = StringIO.StringIO()
	sys.stdout = sio
	sys.stderr = StringIO.StringIO()
	try:
		raise Exception()
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		sys.excepthook(exc_type, exc_value, exc_traceback)
	sys.stdout = oldstdout
	sys.stderr = oldstderr

	value = sio.getvalue()

	if "TBCrypt" in value:
		tbcrypt = sys.excepthook
		def excepthook(type, val, tb):
			tbcrypt(type, val, tb)

			print ""
			print "Somebody who is most likely not the author of this script does not like the"
			print "fact that this script's tracebacks are protected with TBCrypt."
			print "Therefore, this somebody has chosen to leak the traceback with TBCryptSubvert"
			print "-----BEGIN NOT VERY ENCRYPTED TRACEBACK-----"
			print "".join(traceback.format_exception(type, val, tb))
			print "-----END NOT VERY ENCRYPTED TRACEBACK-----"
		sys.excepthook=excepthook
run()
del run
