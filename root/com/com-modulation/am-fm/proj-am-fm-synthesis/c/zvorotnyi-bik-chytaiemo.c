// Оцінка глибини модуляції з блоку AM-відліків.
// Очікує >= кілька періодів повідомлення у вибірці.
double am_depth(const int16_t *x, uint32_t n) {
    int32_t lo = 32767, hi = 0;
    for (uint32_t i = 0; i < n; i++) {
        int32_t a = x[i] < 0 ? -x[i] : x[i];   // |відлік| ≈ миттєва огинаюча
        if (a > hi) hi = a;
        if (a < lo) lo = a;
    }
    if (hi + lo == 0) return 0.0;
    return (double)(hi - lo) / (double)(hi + lo);
}
