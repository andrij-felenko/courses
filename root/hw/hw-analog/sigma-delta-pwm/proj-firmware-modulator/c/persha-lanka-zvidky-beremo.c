#include <stdint.h>
#include <math.h>

#define SINE_POINTS   256u          // точок на період синуса (степінь 2 — навмисне)
#define SINE_MID      128           // 0 синуса лягає на середину шкали
#define SINE_AMP      120           // амплітуда (трохи менша за 128 — лишаємо запас)

static uint8_t sine_tab[SINE_POINTS];

// Викликати ОДИН раз на старті, поза будь-яким перериванням.
void sine_table_init(void)
{
    for (uint16_t i = 0; i < SINE_POINTS; ++i) {
        double phase = 2.0 * M_PI * (double)i / (double)SINE_POINTS;
        double s     = sin(phase);                 // -1 .. +1
        // Перенесли в діапазон рівня 0..255: середина 128 + амплітуда·синус.
        sine_tab[i] = (uint8_t)(SINE_MID + SINE_AMP * s + 0.5);
    }
}
