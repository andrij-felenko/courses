# benchmark_ffi.py
import time
import ctypes
import os
import array
from cffi import FFI

# 1. Налаштування ctypes
lib_path = os.path.abspath("./libfastmath.so")
ctypes_lib = ctypes.CDLL(lib_path)

ctypes_lib.fast_crc32_step.argtypes = [ctypes.c_uint32, ctypes.c_uint8]
ctypes_lib.fast_crc32_step.restype = ctypes.c_uint32

ctypes_lib.vector_scale.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t, ctypes.c_double]
ctypes_lib.vector_scale.restype = None

class CtypesPoint3D(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
        ("id", ctypes.c_uint32),
    ]

ctypes_lib.transform_point.argtypes = [
    ctypes.POINTER(CtypesPoint3D),
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double
]
ctypes_lib.transform_point.restype = None

# 2. Налаштування cffi (ABI Mode)
ffi_abi = FFI()
ffi_abi.cdef("""
    typedef struct { double x, y, z; uint32_t id; } Point3D;
    uint32_t fast_crc32_step(uint32_t crc, uint8_t byte);
    void vector_scale(double *data, size_t size, double factor);
    void transform_point(Point3D *pt, double dx, double dy, double dz);
""")
cffi_abi_lib = ffi_abi.dlopen(lib_path)

# 3. Імпорт cffi (API Mode Out-of-line)
try:
    from _fastmath_cffi import ffi as ffi_api, lib as cffi_api_lib
except ImportError:
    cffi_api_lib = None

# Еталонна реалізація алгоритму на чистому Python
def py_crc32_step(crc, byte):
    crc ^= byte
    for _ in range(8):
        crc = (crc >> 1) ^ (0xEDB88320 if (crc & 1) else 0)
    return crc & 0xFFFFFFFF


def benchmark_scalar(iterations=1_000_000):
    print(f"--- Бенчмарк 1: Скалярний виклик fast_crc32 ({iterations:,} ітерацій) ---")
    
    # 1. Pure Python
    t0 = time.perf_counter_ns()
    crc = 0xFFFFFFFF
    for _ in range(iterations):
        crc = py_crc32_step(crc, 0xAB)
    t_py = (time.perf_counter_ns() - t0) / iterations
    print(f"Чистий Python:          {t_py:6.2f} нс/виклик")

    # 2. ctypes
    t0 = time.perf_counter_ns()
    crc = 0xFFFFFFFF
    for _ in range(iterations):
        crc = ctypes_lib.fast_crc32_step(crc, 0xAB)
    t_ctypes = (time.perf_counter_ns() - t0) / iterations
    print(f"ctypes (libffi):        {t_ctypes:6.2f} нс/виклик")

    # 3. cffi ABI
    t0 = time.perf_counter_ns()
    crc = 0xFFFFFFFF
    for _ in range(iterations):
        crc = cffi_abi_lib.fast_crc32_step(crc, 0xAB)
    t_cffi_abi = (time.perf_counter_ns() - t0) / iterations
    print(f"cffi (ABI In-line):     {t_cffi_abi:6.2f} нс/виклик")

    # 4. cffi API Out-of-line
    if cffi_api_lib:
        t0 = time.perf_counter_ns()
        crc = 0xFFFFFFFF
        for _ in range(iterations):
            crc = cffi_api_lib.fast_crc32_step(crc, 0xAB)
        t_cffi_api = (time.perf_counter_ns() - t0) / iterations
        print(f"cffi (API Out-of-line): {t_cffi_api:6.2f} нс/виклик")


def benchmark_struct_mutation(iterations=500_000):
    print(f"\n--- Бенчмарк 2: Передача структури за покажчиком ({iterations:,} ітерацій) ---")
    
    # ctypes
    pt_ctypes = CtypesPoint3D(1.0, 2.0, 3.0, 0)
    t0 = time.perf_counter_ns()
    for _ in range(iterations):
        ctypes_lib.transform_point(ctypes.byref(pt_ctypes), 0.1, 0.2, 0.3)
    t_ctypes = (time.perf_counter_ns() - t0) / iterations
    print(f"ctypes (byref struct):  {t_ctypes:6.2f} нс/виклик")

    # cffi API
    if cffi_api_lib:
        pt_cffi = ffi_api.new("Point3D *", [1.0, 2.0, 3.0, 0])
        t0 = time.perf_counter_ns()
        for _ in range(iterations):
            cffi_api_lib.transform_point(pt_cffi, 0.1, 0.2, 0.3)
        t_cffi_api = (time.perf_counter_ns() - t0) / iterations
        print(f"cffi API (new struct):  {t_cffi_api:6.2f} нс/виклик")


def benchmark_vector_memory(size=100_000, runs=1_000):
    print(f"\n--- Бенчмарк 3: Векторна обробка масиву {size:,} елементів ({runs} прогонів) ---")
    
    raw_data = array.array("d", [1.0] * size)

    # 1. ctypes через каст масиву from_buffer
    t0 = time.perf_counter_ns()
    for _ in range(runs):
        c_arr = (ctypes.c_double * size).from_buffer(raw_data)
        ctypes_lib.vector_scale(c_arr, size, 1.001)
    t_ctypes_buf = (time.perf_counter_ns() - t0) / runs / 1000
    print(f"ctypes (from_buffer zero-copy): {t_ctypes_buf:6.2f} мкс/прогін")

    # 2. cffi API через ffi.from_buffer
    if cffi_api_lib:
        t0 = time.perf_counter_ns()
        for _ in range(runs):
            c_buf = ffi_api.from_buffer("double[]", raw_data)
            cffi_api_lib.vector_scale(c_buf, size, 1.001)
        t_cffi_api_buf = (time.perf_counter_ns() - t0) / runs / 1000
        print(f"cffi API (ffi.from_buffer):     {t_cffi_api_buf:6.2f} мкс/прогін")


if __name__ == "__main__":
    benchmark_scalar()
    benchmark_struct_mutation()
    benchmark_vector_memory()
