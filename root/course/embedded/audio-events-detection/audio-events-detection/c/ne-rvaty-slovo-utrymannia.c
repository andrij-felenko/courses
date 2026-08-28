#include <stdbool.h>

static bool  active   = false;    // стан: чи триває подія
static int   hang     = 0;        // лічильник хвоста, кадрів
static float noise    = 50.0f;    // оцінка фону

const float ALPHA    = 0.02f;
const float K_UP     = 4.0f;      // запас на ВХІД (вищий поріг)
const float K_DOWN   = 2.0f;      // запас на ВИХІД (нижчий поріг)
const int   HANG     = 12;        // хвіст ≈ 12 кадрів утримання

bool vad_step(float rms) {
    float thr_up   = noise * K_UP;
    float thr_down = noise * K_DOWN;

    if (!active) {                         // зараз тиша
        if (rms > thr_up) {                // впевнено пробили верхній поріг
            active = true;
            hang   = HANG;                 // зарядили хвіст
        } else {
            noise += ALPHA * (rms - noise); // фон оновлюємо лише в тиші
        }
    } else {                               // зараз подія
        if (rms > thr_down) {              // ще досить гучно — продовжуємо
            hang = HANG;                   // перезарядили хвіст
        } else if (--hang <= 0) {          // тихо й хвіст вичерпано
            active = false;                // подія скінчилась
        }
    }
    return active;
}
