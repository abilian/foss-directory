# add devtools `debug` function to builtins

debug = None
try:
    from devtools import debug
except ImportError:
    pass


def install():
    if debug:
        __builtins__["debug"] = debug
