import ctypes

lib = ctypes.CDLL("./libmath_ops.so")

# Обов'язкове налаштування сигнатури: restype та argtypes
lib.add_vectors.restype = ctypes.c_int32
lib.add_vectors.argtypes = [
    ctypes.POINTER(ctypes.c_int32),
    ctypes.POINTER(ctypes.c_int32),
    ctypes.POINTER(ctypes.c_int32),
    ctypes.c_size_t,
]

size = 4
arr_type = ctypes.c_int32 * size
vec_a = arr_type(1, 2, 3, 4)
vec_b = arr_type(10, 20, 30, 40)
vec_out = arr_type()

ret = lib.add_vectors(vec_a, vec_b, vec_out, size)
# vec_out містить результат [11, 22, 33, 44]
