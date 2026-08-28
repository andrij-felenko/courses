// Boost-драйвер послідовної гірлянди: перевіряємо, чи кратність у робочій зоні.
// M > ~6…8 (D > ~0.85) — простий boost видихається: бери трансформатор
// або розбий гірлянду на дві коротші.
#include <stdio.h>

void led_boost_check(int n_leds, float vf, float vin) {
    float vout = n_leds * vf;
    float M    = vout / vin;
    float D    = 1.0f - 1.0f / M;      // з M = 1/(1−D)
    printf("%d LED: Vout=%.1f В  M=%.2f  D=%.2f  -> %s\n",
           n_leds, vout, M, D,
           (D > 0.85f) ? "МЕЖА boost: трансформатор або дві гілки"
                       : "простий boost ОК");
}

int main(void) {
    led_boost_check(8,  3.2f, 5.0f);   // на верхньому краю — ще ОК
    led_boost_check(12, 3.2f, 5.0f);   // за межею — треба інше рішення
    return 0;
}
