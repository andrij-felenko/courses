import ctypes
import numpy as np

# Завантаження динамічної бібліотеки
lib = ctypes.CDLL("./libmatrix_perm.so")

# Визначення аргументів та типу повернення
lib.perm_compute_u64.argtypes = [
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_uint64)
]
lib.perm_compute_u64.restype = ctypes.c_int

def compute_permanent(mat: np.ndarray) -> int:
    n = mat.shape[0]
    mat_flat = mat.astype(np.uint64).flatten()
    c_arr = mat_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
    res = ctypes.c_uint64(0)
    
    status = lib.perm_compute_u64(c_arr, n, None, ctypes.byref(res))
    if status != 0:
        raise RuntimeError(f"Error computing permanent: code {status}")
    return res.value
