import ctypes

class SieveConfig(ctypes.Structure):
    _fields_ = [
        ("start_n", ctypes.c_uint64),
        ("end_n", ctypes.c_uint64),
        ("segment_size", ctypes.c_uint32),
        ("thread_count", ctypes.c_uint32),
        ("wheel", ctypes.c_int),
        ("count_only", ctypes.c_bool),
    ]

class SieveResult(ctypes.Structure):
    _fields_ = [
        ("total_primes", ctypes.c_uint64),
        ("execution_us", ctypes.c_uint64),
        ("bytes_allocated", ctypes.c_uint64),
        ("primes_array", ctypes.POINTER(ctypes.c_uint64)),
        ("array_capacity", ctypes.c_size_t),
    ]

# Завантаження спільної бібліотеки libsieve.so
libsieve = ctypes.CDLL("./libsieve.so")
libsieve.sieve_execute.argtypes = [ctypes.POINTER(SieveConfig), ctypes.POINTER(SieveResult)]
libsieve.sieve_free_result.argtypes = [ctypes.POINTER(SieveResult)]
