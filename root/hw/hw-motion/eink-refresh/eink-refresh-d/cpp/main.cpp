#define FULL_EVERY 20            // повне оновлення кожні 20 часткових
static uint8_t partial_count = 0;

// Викликається раз на хвилину з готовим образом кадру
void clock_tick(const uint8_t *frame) {
    if (partial_count == 0) {
        epd_update(frame, EPD_FULL);     // чисте повне: змиває привид
    } else {
        epd_update(frame, EPD_PARTIAL);  // швидко, без блимання
    }
    partial_count++;
    if (partial_count >= FULL_EVERY)
        partial_count = 0;               // наступний кадр знову повний
}
