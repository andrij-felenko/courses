// Період кадру в мс: інтервал між сусідніми кадрами.
float frame_period_ms(int fps) {
    return 1000.0f / (float)fps;   // ПАСТКА: 1000/fps цілими — нижче
}

// Сума обчислювальних ланок (без радіо) — те, що мусить влізти в період кадру.
// Беремо ВЕРХНЮ межу: дедлайн перевіряють за найгіршим випадком.
float compute_load_ms(const fpv_system *s) {
    return s->sensor.hi + s->encode.hi + s->decode.hi + s->display.hi;
}

// Чи влазить обробка кадру в період? true = встигаємо.
bool fits_frame_deadline(const fpv_system *s) {
    return compute_load_ms(s) <= frame_period_ms(s->fps);
}
