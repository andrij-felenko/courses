import ctypes

class HorseshoePoint2D(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

class HorseshoeConfig(ctypes.Structure):
    _fields_ = [("alpha", ctypes.c_double), ("beta", ctypes.c_double)]

lib = ctypes.CDLL("./libhorseshoe.so")
lib.horseshoe_init_config.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.POINTER(HorseshoeConfig)]
lib.horseshoe_init_config.restype = ctypes.c_int
