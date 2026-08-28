# Обмін: швидкість проти свіжості. Кеш прискорює, але між оновленнями
# віддає трохи застарілий результат.
_cached_c = 0.0
_cached_raw = 0xFFFF                          # «нема чинного кешу»

def to_celsius(raw):
    global _cached_c, _cached_raw
    if raw == _cached_raw:
        return _cached_c                      # швидкий шлях: без обчислень
    _cached_c = expensive_convert(raw)        # повільний шлях: рахуємо
    _cached_raw = raw
    return _cached_c
