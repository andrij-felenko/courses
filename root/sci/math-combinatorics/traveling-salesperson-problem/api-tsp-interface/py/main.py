import ctypes

class TSPResult(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_int),
        ("tour_cost", ctypes.c_double),
        ("tour", ctypes.POINTER(ctypes.c_int)),
        ("tour_size", ctypes.c_size_t),
        ("elapsed_time_sec", ctypes.c_double),
        ("nodes_evaluated", ctypes.c_uint64)
    ]
