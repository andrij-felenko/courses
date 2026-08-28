import ctypes
import numpy as np

# Завантаження скомпільованої динамічної бібліотеки (.so на Linux або .dll на Windows)
lib = ctypes.CDLL("./libphasefield.so")

class PFConfig(ctypes.Structure):
    _fields_ = [
        ("nx", ctypes.c_size_t),
        ("ny", ctypes.c_size_t),
        ("dx", ctypes.c_double),
        ("dt", ctypes.c_double),
        ("kappa", ctypes.c_double),
        ("mobility", ctypes.c_double),
        ("use_openmp", ctypes.c_int)
    ]

# Специфікація типів аргументів та повернутих значень
lib.pf_grid_create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(PFConfig)]
lib.pf_grid_create.restype = ctypes.c_int

lib.pf_step_explicit.argtypes = [ctypes.c_void_p]
lib.pf_step_explicit.restype = ctypes.c_int

# Створення об'єкта та запуск 1000 кроків симуляції
cfg = PFConfig(nx=256, ny=256, dx=1.0, dt=0.02, kappa=1.0, mobility=1.0, use_openmp=1)
grid_ptr = ctypes.c_void_p()
lib.pf_grid_create(ctypes.byref(grid_ptr), ctypes.byref(cfg))

for step in range(1000):
    lib.pf_step_explicit(grid_ptr)
