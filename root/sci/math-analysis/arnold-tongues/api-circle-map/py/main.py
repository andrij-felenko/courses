import ctypes

class CircleMapConfig(ctypes.Structure):
    _fields_ = [
        ("omega", ctypes.c_double),
        ("k", ctypes.c_double),
        ("transient_steps", ctypes.c_size_t),
        ("measure_steps", ctypes.c_size_t),
        ("initial_x", ctypes.c_double)
    ]

class CircleMapResult(ctypes.Structure):
    _fields_ = [
        ("rotation_number", ctypes.c_double),
        ("numerator", ctypes.c_int),
        ("denominator", ctypes.c_int),
        ("is_locked", ctypes.c_bool),
        ("lyapunov_exponent", ctypes.c_double)
    ]

# Завантаження бібліотеки
lib = ctypes.CDLL("./libcirclemap.so")
lib.circle_map_solve.argtypes = [
    ctypes.POINTER(CircleMapConfig),
    ctypes.c_int,
    ctypes.c_double,
    ctypes.POINTER(CircleMapResult)
]
lib.circle_map_solve.restype = ctypes.c_int
