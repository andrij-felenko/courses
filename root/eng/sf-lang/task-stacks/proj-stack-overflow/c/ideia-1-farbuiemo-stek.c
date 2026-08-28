// заповнюємо область відомим візерунком на старті
static const uint8_t CANARY = 0xA5;
void paint(uint8_t *base, size_t n) {
    for (size_t i = 0; i < n; i++) base[i] = CANARY;
}

// глибина використання = скільки патерну затерто з «дна» вгору
size_t used_from_pattern(const uint8_t *base, size_t n) {
    size_t free_bytes = 0;
    while (free_bytes < n && base[free_bytes] == CANARY) free_bytes++;
    return n - free_bytes;   // байтів, яких торкалися
}
