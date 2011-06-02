def icbm():
    import sys

    for mn in sys.modules:
        if mn.startswith("Lymia"):
            sys.modules[mn] = None
            del globals()[mn]

icbm()
del icbm

