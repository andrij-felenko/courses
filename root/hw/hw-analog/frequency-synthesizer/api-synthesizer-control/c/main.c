#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Макроси адрес регістрів */
#define PLL_REG0 0
#define PLL_REG1 1
#define PLL_REG2 2
#define PLL_REG3 3
#define PLL_REG4 4
#define PLL_REG5 5

/* Структура конфігурації синтезатора */
typedef struct {
    uint32_t regs[6];     /* Обраховані 32-бітні значення R0..R5 */
    double actual_freq_hz;/* Фактично сформована частота */
} pll_synth_driver_t;

/* Прототип зовнішньої функції запису SPI */
extern void spi_write_32bit(uint32_t data);

/* Функція розрахунку регістрів для заданої частоти */
bool pll_synth_tune(pll_synth_driver_t *drv, double target_freq_hz, double ref_osc_hz) {
    if (!drv || target_freq_hz < 35.0e6 || target_freq_hz > 4400.0e6 || ref_osc_hz <= 0.0) {
        return false;
    }

    /* 1. Визначення вихідного дільника RF_DIV (1, 2, 4, 8, 16, 32, 64) */
    uint32_t rf_div = 1;
    uint32_t rf_div_select = 0;
    double vco_freq = target_freq_hz;

    while (vco_freq < 2200.0e6 && rf_div_select < 6) {
        vco_freq *= 2.0;
        rf_div *= 2;
        rf_div_select++;
    }

    /* 2. Фіксований R-дільник = 1, MOD = 4000 (для кроку) */
    uint32_t r_div = 1;
    uint32_t mod = 4000;
    double f_pfd = ref_osc_hz / r_div;

    /* 3. Розрахунок INT та FRAC */
    double n_total = vco_freq / f_pfd;
    uint32_t integer_part = (uint32_t)floor(n_total);
    uint32_t frac_part = (uint32_t)round((n_total - (double)integer_part) * (double)mod);

    if (frac_part >= mod) {
        integer_part++;
        frac_part = 0;
    }

    /* Обчислення фактичної частоти */
    drv->actual_freq_hz = ((double)integer_part + ((double)frac_part / (double)mod)) * f_pfd / (double)rf_div;

    /* 4. Збирання регістрів R0..R5 */
    drv->regs[0] = (integer_part << 15) | (frac_part << 3) | PLL_REG0;
    drv->regs[1] = (1u << 27) | (mod << 3) | PLL_REG1;                  /* Prescaler 8/9 */
    drv->regs[2] = (7u << 9) | (r_div << 3) | (1u << 6) | PLL_REG2;     /* CP = 2.5mA, PD_pol = positive */
    drv->regs[3] = (1u << 15) | (100u << 3) | PLL_REG3;                 /* Clock div = 100 */
    drv->regs[4] = (rf_div_select << 20) | (1u << 5) | (3u << 3) | PLL_REG4; /* Output Power +5dBm, RF_EN */
    drv->regs[5] = (1u << 22) | (3u << 16) | PLL_REG5;                  /* Digital Lock Detect */

    return true;
}

/* Функція послідовного запису регістрів через SPI (від R5 до R0) */
void pll_synth_commit(const pll_synth_driver_t *drv) {
    if (!drv) return;
    for (int i = 5; i >= 0; i--) {
        spi_write_32bit(drv->regs[i]);
    }
}
