#include <stdint.h>

#define GPIOA_BSRR   (*(volatile uint32_t *)(0x40010800u + 0x10u))
#define TIM2_SR      (*(volatile uint32_t *)(0x40000000u + 0x10u))

extern const uint32_t sine_bsrr[256];   /* згенерована таблиця слів BSRR */

static uint32_t          phase;         /* накопичувач фази: чіпає лише переривання */
static volatile uint32_t step;          /* настроювальне слово: пише головний цикл  */

/* Перерахувати частоту в настроювальне слово.
   f подається в мілігерцах, щоб не тягти в прошивку дробову арифметику.  */
static uint32_t tuning_word(uint32_t f_millihz, uint32_t fs_hz)
{
    uint64_t denom = (uint64_t)fs_hz * 1000u;
    return (uint32_t)((((uint64_t)f_millihz << 32) + denom / 2u) / denom);
}

void dac_set_freq(uint32_t f_millihz, uint32_t fs_hz)
{
    step = tuning_word(f_millihz, fs_hz);   /* 32-бітний запис неподільний — без критичної секції */
}

void TIM2_IRQHandler(void)
{
    TIM2_SR = ~1u;                          /* зняти прапорець оновлення */
    phase += step;                          /* крок фази                 */
    GPIOA_BSRR = sine_bsrr[phase >> 24];    /* усе перетворення — оцей рядок */
}
