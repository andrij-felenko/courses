// добуток двох Q15 → назад у Q15, через 32-бітний проміжок і зсув
static inline int16_t qmul(int16_t a, int16_t b) {
    int32_t p = (int32_t)a * (int32_t)b;   // Q15·Q15 = Q30, у 32 бітах
    return (int16_t)(p >> 15);             // повертаємо кому на місце
}

// множення кватерніонів у Q15 (акумулятор 32-бітний, зсув наприкінці)
quat_q15 quat_mul_q15(quat_q15 a, quat_q15 b) {
    int32_t w = (int32_t)a.w*b.w - (int32_t)a.x*b.x - (int32_t)a.y*b.y - (int32_t)a.z*b.z;
    int32_t x = (int32_t)a.w*b.x + (int32_t)a.x*b.w + (int32_t)a.y*b.z - (int32_t)a.z*b.y;
    int32_t y = (int32_t)a.w*b.y - (int32_t)a.x*b.z + (int32_t)a.y*b.w + (int32_t)a.z*b.x;
    int32_t z = (int32_t)a.w*b.z + (int32_t)a.x*b.y - (int32_t)a.y*b.x + (int32_t)a.z*b.w;
    quat_q15 r = { (int16_t)(w >> 15), (int16_t)(x >> 15),
                   (int16_t)(y >> 15), (int16_t)(z >> 15) };
    return r;
}
