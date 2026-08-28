// Обмін: швидкість проти свіжості. Кеш прискорює, але між оновленнями
// віддає трохи застарілий результат.
static float          cached_c;
static std::uint16_t  cached_raw = 0xFFFF;   // «нема чинного кешу»

float to_celsius(std::uint16_t raw) {
    if (raw == cached_raw) return cached_c;   // швидкий шлях: без обчислень
    cached_c   = expensive_convert(raw);      // повільний шлях: рахуємо
    cached_raw = raw;
    return cached_c;
}
