#include <math.h>
#include <stdint.h>

// Роздільність повзунка яскравості (окремо від роздільності duty!).
#define DIM_LEVELS   256                 // положення 0..255
#define DIM_GAMMA    2.2f                // ≈ сприйняття ока

// Таблиця: положення повзунка → гамма-скоригований duty.
static uint16_t g_gamma_lut[DIM_LEVELS];

// Порахувати таблицю раз при старті.  duty = MAX · (level/(LEVELS-1))^γ
static void dim_gamma_build(void) {
    for (int i = 0; i < DIM_LEVELS; i++) {
        float x = (float)i / (float)(DIM_LEVELS - 1);        // 0.0 .. 1.0
        float d = powf(x, DIM_GAMMA) * (float)DIM_DUTY_MAX;
        // округлення до найближчого; нуль лишається нулем (повне гасіння)
        g_gamma_lut[i] = (uint16_t)(d + 0.5f);
    }
    // Гарантуємо монотонність і крайні точки навіть за похибок округлення.
    g_gamma_lut[0]             = 0;
    g_gamma_lut[DIM_LEVELS-1]  = DIM_DUTY_MAX;
}

// Задати яскравість каналу за положенням повзунка (0..255), плавно за ms.
static void dim_set_level(const dim_ch_t *ch, uint8_t level, int ms) {
    uint16_t duty = g_gamma_lut[level];          // гамма вже врахована
    dim_fade_to(ch, duty, ms);                   // і одразу плавний перехід
}
