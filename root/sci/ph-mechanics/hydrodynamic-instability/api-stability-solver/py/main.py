import ctypes
import numpy as np

# Завантаження динамічної бібліотеки .so / .dll
lib = ctypes.CDLL("./libhydro_stability.so")

# Визначення типів
class HydroGridConfig(ctypes.Structure):
    _fields_ = [
        ("N", ctypes.c_int),
        ("Re", ctypes.c_double),
        ("Ra", ctypes.c_double),
        ("Pr", ctypes.c_double),
        ("We", ctypes.c_double),
        ("beta_fs", ctypes.c_double),
        ("atwood", ctypes.c_double),
        ("delta_v", ctypes.c_double),
        ("alpha", ctypes.c_double),
        ("beta", ctypes.c_double),
        ("bc_type", ctypes.c_int),
        ("solver", ctypes.c_int),
        ("shift_real", ctypes.c_double),
        ("shift_imag", ctypes.c_double)
    ]

# Налаштування аргументів функцій
lib.hydro_profile_create_poiseuille.argtypes = [ctypes.POINTER(HydroGridConfig), ctypes.POINTER(ctypes.c_void_p)]
lib.hydro_profile_create_poiseuille.restype = ctypes.c_int

print("Python ctypes integration initialized successfully.")
