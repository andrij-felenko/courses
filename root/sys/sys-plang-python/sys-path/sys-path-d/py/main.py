import sys
import math
import random

def inspect_module_origins():
    print(f"sys.path[0]: {sys.path[0]}")
    for name in ["math", "random", "os", "sys"]:
        if name in sys.modules:
            mod = sys.modules[name]
            origin = getattr(mod, "__file__", None) or getattr(getattr(mod, "__spec__", None), "origin", "built-in")
            print(f"Модуль '{name}': origin = {origin}")

inspect_module_origins()
