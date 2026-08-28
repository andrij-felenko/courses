import ctypes
import os
import platform

# 1. Завантаження DSO/DLL бібліотеки
lib_name = "bridge_core.dll" if platform.system() == "Windows" else "./libbridge_core.so"
lib = ctypes.CDLL(os.path.abspath(lib_name))

# 2. Опис C-структури з точним порядком і розміром полів
class BridgeConfig(ctypes.Structure):
    _fields_ = [
        ("sample_rate", ctypes.c_int32),
        ("channels", ctypes.c_int32),
        ("scale_factor", ctypes.c_double),
        ("enable_filter", ctypes.c_uint8),
        ("padding", ctypes.c_uint8 * 7),
    ]

# 3. Налаштування сигнатур (argtypes та restype)
lib.bridge_create_context.argtypes = [ctypes.POINTER(BridgeConfig), ctypes.POINTER(ctypes.c_void_p)]
lib.bridge_create_context.restype = ctypes.c_int

lib.bridge_process_buffer.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
    ctypes.POINTER(ctypes.c_size_t)
]
lib.bridge_process_buffer.restype = ctypes.c_int

lib.bridge_free_buffer.argtypes = [ctypes.POINTER(ctypes.c_float)]
lib.bridge_free_buffer.restype = None

lib.bridge_free_context.argtypes = [ctypes.c_void_p]
lib.bridge_free_context.restype = None

lib.bridge_get_last_error.argtypes = [ctypes.c_int]
lib.bridge_get_last_error.restype = ctypes.c_char_p

# 4. Виконання виклику з гарантованим очищенням ресурсів
config = BridgeConfig(sample_rate=48000, channels=2, scale_factor=1.5, enable_filter=1)
ctx = ctypes.c_void_p()

status = lib.bridge_create_context(ctypes.byref(config), ctypes.byref(ctx))
if status != 0:
    err_msg = lib.bridge_get_last_error(status).decode("utf-8")
    raise RuntimeError(f"FFI Помилка створення контексту: {err_msg}")

try:
    input_array = (ctypes.c_float * 4)(1.0, 2.0, 3.0, 4.0)
    out_buf = ctypes.POINTER(ctypes.c_float)()
    out_len = ctypes.c_size_t()

    res = lib.bridge_process_buffer(ctx, input_array, len(input_array), ctypes.byref(out_buf), ctypes.byref(out_len))
    if res != 0:
        err_msg = lib.bridge_get_last_error(res).decode("utf-8")
        raise RuntimeError(f"FFI Помилка обробки: {err_msg}")

    try:
        # Копіюємо дані у стандартний список Python
        result = [out_buf[i] for i in range(out_len.value)]
        print(f"Результат обробки ({out_len.value} елементів): {result}")
    finally:
        # Звільняємо буфер виключно через рідну функцію бібліотеки!
        lib.bridge_free_buffer(out_buf)
finally:
    # Звільняємо контекст
    lib.bridge_free_context(ctx)
