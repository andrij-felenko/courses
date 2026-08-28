#include <stdint.h>

typedef struct {
    uint32_t rate;        // поточний цільовий бітрейт, біт/с
    uint32_t rate_min;    // підлога: нижче не опускаємось (гірша допустима якість)
    uint32_t rate_max;    // стеля: вище не піднімаємось (краща потрібна якість)

    // пороги втрат у ПРОМІЛЕ (‰), щоб лишитись у цілій арифметиці:
    //   20‰ = 2%   (поріг росту),   100‰ = 10%  (поріг падіння)
    uint16_t loss_up_permille;    // < цього → рости
    uint16_t loss_down_permille;  // > цього → падати

    uint8_t  up_step_pct;   // крок угору, % (наприклад, 5 → ×1.05)
} abr_t;

void abr_init(abr_t *c, uint32_t start, uint32_t lo, uint32_t hi)
{
    c->rate     = start;
    c->rate_min = lo;
    c->rate_max = hi;
    c->loss_up_permille   = 20;   // 2.0%
    c->loss_down_permille = 100;  // 10.0%
    c->up_step_pct        = 5;    // +5% за крок угору
}
