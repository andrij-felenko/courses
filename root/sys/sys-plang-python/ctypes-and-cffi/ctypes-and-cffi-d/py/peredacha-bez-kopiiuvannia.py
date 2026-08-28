import ctypes

# Створюємо мутабельний байтовий буфер розміром 1 МБ
buffer_data = bytearray(1024 * 1024)

# Отримуємо обгортку ctypes над тим самим блоком пам'яті (без копіювання!)
c_buffer = (ctypes.c_uint8 * len(buffer_data)).from_buffer(buffer_data)

# Передаємо покажчик нативній C-функції
lib.process_raw_bytes(c_buffer, len(buffer_data))
