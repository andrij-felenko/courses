import ctypes
import os

class CantorInterval(ctypes.Structure):
    _fields_ = [("start", ctypes.c_double), ("end", ctypes.c_double)]

lib = ctypes.CDLL(os.path.abspath("libcantor.so"))
lib.cantor_contains_point.argtypes = [ctypes.c_double, ctypes.c_int]
lib.cantor_contains_point.restype = ctypes.c_bool

def is_in_cantor_set(x: float, depth: int = 30) -> bool:
    return lib.cantor_contains_point(x, depth)
