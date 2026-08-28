// Стара версія функції для клієнтів, зібраних під ENGINE_1.0
int engine_compute_v1(int x) {
    return x * 2;
}
__asm__(".symver engine_compute_v1, engine_compute@ENGINE_1.0");

// Нова версія функції для нових клієнтів (ENGINE_2.0 за замовчуванням)
int engine_compute_v2(int x, int flags) {
    return x * 3 + flags;
}
__asm__(".symver engine_compute_v2, engine_compute@@ENGINE_2.0");
