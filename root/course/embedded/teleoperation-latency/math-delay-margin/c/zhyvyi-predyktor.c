#include <math.h>

typedef struct {
    float x;      // м, положення на площині
    float y;      // м
    float theta;  // рад, курс (0 = вздовж осі X)
} pose_t;

// Прогнати модель ровера вперед на dt секунд за командою (v, w_turn).
// v      — лінійна швидкість, м/с (уперед додатна)
// w_turn — кутова швидкість повороту, рад/с (ліворуч додатна)
// Інтегруємо простим кроком Ейлера — для малих dt (частки секунди) цього досить.
static pose_t rover_predict(pose_t p, float v, float w_turn, float dt) {
    const float STEP = 0.02f;                 // крок інтегрування 20 мс
    for (float t = 0.0f; t < dt; t += STEP) {
        float h = (dt - t < STEP) ? (dt - t) : STEP;   // останній крок — залишок
        p.x     += v * cosf(p.theta) * h;     // рух уздовж поточного курсу
        p.y     += v * sinf(p.theta) * h;
        p.theta += w_turn * h;                // курс повертається
    }
    // нормалізуємо курс у (−π, π], щоб не накопичувати оберти
    while (p.theta >  3.14159265f) p.theta -= 6.28318531f;
    while (p.theta < -3.14159265f) p.theta += 6.28318531f;
    return p;
}

// Куди малювати ФАНТОМ: беремо запізнілу позицію з телеметрії
// й проганяємо її вперед рівно на затримку каналу.
pose_t phantom_pose(pose_t last_known, float v, float w_turn, float latency_s) {
    return rover_predict(last_known, v, w_turn, latency_s);
}
