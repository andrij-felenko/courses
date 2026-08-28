#include <math.h>

/* Чутливість акселерометра з паспорта: ±2g на 16-бітному АЦП
   → 16384 відліки на 1g. */
const float ACCEL_SCALE = 1.0f / 16384.0f;   /* відлік → частки g */

void tilt_from_accel(int16_t rawX, int16_t rawY, int16_t rawZ) {
    /* крок 1: сирі відліки АЦП → частки g */
    float aX = rawX * ACCEL_SCALE;
    float aY = rawY * ACCEL_SCALE;
    float aZ = rawZ * ACCEL_SCALE;

    /* крок 2: довжина вектора — перевірка, чи давач у спокої */
    float mag = sqrtf(aX*aX + aY*aY + aZ*aZ);   /* у спокої має бути ~1.0 g */

    /* крок 3: кути нахилу з проєкцій гравітації (радіани → градуси) */
    float pitch = atan2f(aX, aZ) * 57.2958f;    /* тангаж */
    float roll  = atan2f(aY, aZ) * 57.2958f;    /* крен   */
    /* якщо mag помітно відрізняється від 1g — є рух, нахилу зараз вірити не можна */
}
