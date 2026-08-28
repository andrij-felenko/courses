import ctypes

class PointRecord(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int32),
        ("y", ctypes.c_int32),
        ("weight", ctypes.c_double),
        ("flags", ctypes.c_uint8),
    ]

class FloatIntUnion(ctypes.Union):
    _fields_ = [
        ("as_uint", ctypes.c_uint32),
        ("as_float", ctypes.c_float),
        ("as_bytes", ctypes.c_uint8 * 4),
    ]

# Перевірка розміру пам'яті
p = PointRecord(x=10, y=20, weight=3.14, flags=1)
print(f"Розмір структури: {ctypes.sizeof(p)} байтів")  # Рівно 24 байти
