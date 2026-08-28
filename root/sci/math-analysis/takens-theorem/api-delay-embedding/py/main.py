import ctypes
import numpy as np

# Завантаження динамічної бібліотеки
lib = ctypes.CDLL("./libtakens.so")

# Визначення типів C
class TakensConfig(ctypes.Structure):
    _fields_ = [
        ("max_delay", ctypes.c_size_t),
        ("n_bins", ctypes.c_size_t),
        ("max_embedding_dim", ctypes.c_size_t),
        ("r_tol", ctypes.c_double),
        ("fnn_threshold", ctypes.c_double),
        ("num_threads", ctypes.c_size_t)
    ]

# Налаштування аргументів функцій
lib.takens_config_init_default.argtypes = [ctypes.POINTER(TakensConfig)]
lib.takens_config_init_default.restype = ctypes.c_int

def py_compute_mutual_info(signal: np.ndarray, max_delay: int = 50) -> int:
    signal = np.ascontiguousarray(signal, dtype=np.float64)
    config = TakensConfig()
    lib.takens_config_init_default(ctypes.byref(config))
    config.max_delay = max_delay

    opt_delay = ctypes.c_size_t(0)
    mi_buffer = (ctypes.c_double * max_delay)()

    res = lib.takens_compute_mutual_information(
        signal.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        len(signal),
        ctypes.byref(config),
        mi_buffer,
        ctypes.byref(opt_delay)
    )
    if res == 0:
        return opt_delay.value
    raise RuntimeError(f"Помилка libtakens код: {res}")
