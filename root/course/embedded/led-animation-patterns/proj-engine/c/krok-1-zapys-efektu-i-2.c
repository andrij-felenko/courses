// скільки мс минуло від старту цього проходу, з урахуванням паузи
static uint32_t elapsed(const Anim *a, uint32_t now) {
    uint32_t ref = (a->pausedAt != 0) ? a->pausedAt : now;
    return ref - a->start;          // беззнакова різниця — переповнення millis безпечне
}

// фаза 0..4095 у межах одного проходу; >4095 означає «прохід скінчився»
static uint32_t phaseRaw(const Anim *a, uint32_t now) {
    uint32_t e = elapsed(a, now);
    return (e << 12) / a->duration;   // e/duration · 4096, цілими
}
