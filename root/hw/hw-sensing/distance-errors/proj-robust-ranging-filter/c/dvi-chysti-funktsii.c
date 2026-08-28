// median3 = clamp(c, min(a,b), max(a,b)) — середній з трьох.
static inline uint16_t median3(uint16_t a, uint16_t b, uint16_t c) {
    uint16_t mn = (a < b) ? a : b;     // менше з a,b
    uint16_t mx = (a < b) ? b : a;     // більше з a,b
    return (c < mn) ? mn : (c > mx) ? mx : c;
}

// Сила відлуння → довіра [0..1]: лінійно між підлогою й стелею.
static float confidence(uint16_t s, uint16_t floor, uint16_t full) {
    if (s <= floor) return 0.0f;
    if (s >= full)  return 1.0f;
    return (float)(s - floor) / (float)(full - floor);
}
