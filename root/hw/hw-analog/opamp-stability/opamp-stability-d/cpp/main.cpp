#include <stdio.h>

// Частота, де розімкнене |A| падає до заданого замкненого підсилення G:
//   на ділянці одного полюса |A|·f = GBW (стала площа),
//   тож перетин лінії 1/β настає на f_cross = GBW / G.
static float crossover_hz(float gbw, float gain) {
    return gbw / gain;            // частота зрізу петлі для цього G
}

int main(void) {
    float gbw   = 50.0e6f;        // 50 МГц з даташита
    float f_p2  =  6.0e6f;        // другий полюс — 6 МГц

    float gains[2] = { 4.0f, 1.0f };
    for (int i = 0; i < 2; i++) {
        float fc = crossover_hz(gbw, gains[i]);
        // перетин безпечний, лише якщо він НИЖЧЕ за другий полюс
        // (тоді крива там ще на пологому −20 дБ/дек)
        int safe = (fc < f_p2);
        printf("G=%.0f: f_cross=%.1f MHz  ->  %s\n",
               gains[i], fc / 1e6f,
               safe ? "перетин до p2 -> стійко"
                    : "перетин ЗА p2 -> дзвін!");
    }
    return 0;
}
