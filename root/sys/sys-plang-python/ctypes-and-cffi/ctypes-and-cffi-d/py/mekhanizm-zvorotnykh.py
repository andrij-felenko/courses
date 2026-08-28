import ctypes

# 1. Визначаємо прототип функції: (повертає int, приймає два int)
CMP_FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)

# 2. Пишемо звичайну функцію Python
def my_comparator(a, b):
    return (a > b) - (a < b)

# 3. Створюємо C-покажчик на функцію (C-callable object)
c_callback = CMP_FUNC_TYPE(my_comparator)

# 4. Передаємо в C-бібліотеку
lib.quick_sort(array_ptr, size, c_callback)
