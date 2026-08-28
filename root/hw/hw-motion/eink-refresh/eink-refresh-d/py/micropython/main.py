FULL_EVERY = const(20)           # повне оновлення кожні 20 часткових
partial_count = 0

# Викликається раз на хвилину з готовим образом кадру
def clock_tick(frame):
    global partial_count
    if partial_count == 0:
        epd.update(frame, EPD_FULL)      # чисте повне: змиває привид
    else:
        epd.update(frame, EPD_PARTIAL)   # швидко, без блимання
    partial_count += 1
    if partial_count >= FULL_EVERY:
        partial_count = 0                # наступний кадр знову повний
