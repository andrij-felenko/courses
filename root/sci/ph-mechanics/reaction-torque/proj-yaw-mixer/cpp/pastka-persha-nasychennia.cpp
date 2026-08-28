#include <math.h>

static inline float clampf(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

// Змішувач із коректним насиченням і пріоритетом осей.
// Повертає motor[4] у [0..1]. throttle ∈ [0..1], осі ∈ [−1..+1].
void mix_saturate(float throttle, float roll, float pitch, float yaw,
                  float motor[4])
{
    // 1. Спершу лише моментні канали (без спільного газу).
    //    Це «різницева» частина — вона й нахиляє, і крутить апарат.
    float m[4];
    for (int i = 0; i < 4; ++i) {
        m[i] = MIX[i].roll  * roll
             + MIX[i].pitch * pitch
             + MIX[i].yaw   * yaw;
    }

    // 2. Знайти діапазон різницевої частини по всіх моторах.
    float mmin = m[0], mmax = m[0];
    for (int i = 1; i < 4; ++i) {
        if (m[i] < mmin) mmin = m[i];
        if (m[i] > mmax) mmax = m[i];
    }
    float span = mmax - mmin;   // повний розмах моментної частини

    // 3. Якщо сам розмах уже ширший за вікно [0..1] — момент не влазить
    //    фізично. Стиснути всю моментну частину пропорційно (spread scale).
    //    Тут крен/тангаж/рискання просядуть РАЗОМ, зберігши напрям.
    if (span > 1.0f) {
        float k = 1.0f / span;
        for (int i = 0; i < 4; ++i) m[i] *= k;
        mmin *= k; mmax *= k;
    }

    // 4. Тепер вибрати спільний газ так, щоб уся комбінація влізла.
    //    Дозволений діапазон газу: [ -mmin .. 1 - mmax ].
    //    Бажаний throttle затиснути в цей діапазон — газ «поступається»
    //    моменту, а не навпаки.
    float lo = -mmin;
    float hi = 1.0f - mmax;
    float thr = clampf(throttle, lo, hi);

    // 5. Скласти: газ + моментна частина. Гарантовано в [0..1].
    for (int i = 0; i < 4; ++i)
        motor[i] = clampf(thr + m[i], 0.0f, 1.0f);  // clamp — лише страховка
}
