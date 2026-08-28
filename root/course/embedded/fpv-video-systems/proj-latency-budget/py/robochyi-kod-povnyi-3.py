# Період кадру в мс: інтервал між сусідніми кадрами.
def frame_period_ms(fps: int) -> float:
    return 1000.0 / fps   # ПАСТКА: 1000/fps цілими — нижче

# Сума обчислювальних ланок (без радіо) — те, що мусить влізти в період кадру.
# Беремо ВЕРХНЮ межу: дедлайн перевіряють за найгіршим випадком.
def compute_load_ms(s: FpvSystem) -> float:
    return s.sensor.hi + s.encode.hi + s.decode.hi + s.display.hi

# Чи влазить обробка кадру в період? True = встигаємо.
def fits_frame_deadline(s: FpvSystem) -> bool:
    return compute_load_ms(s) <= frame_period_ms(s.fps)
