# Оголошення типу вказівника на функцію: (restype, *argtypes)
CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)

@CALLBACK_TYPE
def py_comparator(a, b):
    return (a > b) - (a < b)

# Передача у функцію C
lib.register_callback(py_comparator)
# УВАГА: py_comparator повинен утримуватися в пам'яті Python,
# інакше GC збере його і виклик із C призведе до Segmentation Fault.
