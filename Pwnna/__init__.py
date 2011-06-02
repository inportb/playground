def icbm():
    import sys
    for mn in sys.modules:
        if mn.startswith("Lymia"):
            sys.modules[mn] = None
            try:
                del globals()[mn]
            except KeyError:
                pass

icbm()
del icbm

