# ctypes: явне налаштування argtypes та restype
lib_cdecl.calculate_matrix.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.c_double
]
lib_cdecl.calculate_matrix.restype = ctypes.c_int32

# cffi: прямий C-заголовок
ffi.cdef("""
    int calculate_matrix(double *data, size_t rows, size_t cols, double factor);
""")
