# Приклад завантаження та виклику C-API через Python ctypes
import ctypes
from ctypes import c_char_p, c_int, c_size_t, c_uint8, POINTER, c_void_p

lib = ctypes.CDLL("./libengine.so")

# Налаштування сигнатур функцій
lib.engine_create.argtypes = [c_char_p, POINTER(c_void_p)]
lib.engine_create.restype = c_int

lib.engine_destroy.argtypes = [c_void_p]
lib.engine_destroy.restype = None

lib.engine_process.argtypes = [
    c_void_p,
    POINTER(c_uint8),
    c_size_t,
    POINTER(c_uint8),
    POINTER(c_size_t),
]
lib.engine_process.restype = c_int

lib.engine_get_last_error.argtypes = []
lib.engine_get_last_error.restype = c_char_p

# Створення об'єкта
ctx = c_void_p()
st = lib.engine_create(b"XOR-FAST", ctypes.byref(ctx))
if st != 0:
    raise RuntimeError(lib.engine_get_last_error().decode("utf-8"))

try:
    # Обробка даних
    data = (c_uint8 * 4)(0x11, 0x22, 0x33, 0x44)
    out_buf = (c_uint8 * 4)()
    out_len = c_size_t(4)

    st = lib.engine_process(ctx, data, 4, out_buf, ctypes.byref(out_len))
    if st != 0:
        raise RuntimeError(lib.engine_get_last_error().decode("utf-8"))

    print(f"[Python Client] Результат: {[hex(x) for x in out_buf]}")
finally:
    lib.engine_destroy(ctx)
