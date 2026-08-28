/* C Implementation */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define MODULUS_FIXED 4095U  /* 12-бітний модуль дробової частини */

typedef struct {
    uint32_t f_ref_hz;   /* Частота опорного TCXO, Гц */
    uint32_t f_min_vco;  /* Мінімальна частота VCO (напр. 2200 МГц) */
    uint32_t f_max_vco;  /* Максимальна частота VCO (напр. 4400 МГц) */
} pll_config_t;

typedef struct {
    uint32_t int_val;    /* Ціле значення N */
    uint32_t frac_val;   /* Чисельник FRAC */
    uint32_t mod_val;    /* Знаменник MOD */
    uint32_t rf_div;     /* Коефіцієнт RF_DIV (1, 2, 4, ...) */
    uint32_t actual_hz;  /* Фактично отримана частота f_LO */
} pll_settings_t;

static uint64_t gcd64(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t t = b;
        b = a % b;
        a = t;
    }
    return a;
}

bool pll_calculate_lo(const pll_config_t* cfg, uint32_t target_hz, pll_settings_t* out) {
    if (!cfg || !out || target_hz == 0) return false;

    /* 1. Підбір вихідного дільника RF_DIV для входу в діапазон VCO */
    uint32_t rf_div = 1;
    uint64_t vco_freq = (uint64_t)target_hz;

    while (vco_freq < cfg->f_min_vco && rf_div <= 64) {
        rf_div *= 2;
        vco_freq = (uint64_t)target_hz * rf_div;
    }

    if (vco_freq > cfg->f_max_vco) {
        return false; /* Частота поза межами генератора VCO */
    }

    /* 2. Обчислення цілої та дробової частин */
    uint64_t pfd_freq = cfg->f_ref_hz;
    uint32_t int_part = (uint32_t)(vco_freq / pfd_freq);
    uint64_t remainder = vco_freq % pfd_freq;

    /* 3. Розрахунок FRAC при фіксованому MOD */
    uint64_t frac_part = (remainder * MODULUS_FIXED) / pfd_freq;
    uint32_t mod_part = MODULUS_FIXED;

    /* 4. Скорочення дробу FRAC / MOD через наибольший спільний дільник */
    if (frac_part > 0) {
        uint64_t g = gcd64(frac_part, mod_part);
        frac_part /= g;
        mod_part /= (uint32_t)g;
    } else {
        mod_part = 1;
    }

    /* 5. Обчислення фактичної реалізованої частоти */
    uint64_t calc_vco = (uint64_t)int_part * pfd_freq + (pfd_freq * frac_part) / mod_part;
    uint32_t actual_lo = (uint32_t)(calc_vco / rf_div);

    out->int_val = int_part;
    out->frac_val = (uint32_t)frac_part;
    out->mod_val = mod_part;
    out->rf_div = rf_div;
    out->actual_hz = actual_lo;

    return true;
}

int main(void) {
    pll_config_t chip = {
        .f_ref_hz = 26000000U,      /* TCXO 26 МГц */
        .f_min_vco = 2200000000U,   /* VCO Min 2.2 ГГц */
        .f_max_vco = 4400000000U    /* VCO Max 4.4 ГГц */
    };
    pll_settings_t res;

    uint32_t desired_lo = 433920000U; /* 433.92 МГц для LPD/LoRa */

    if (pll_calculate_lo(&chip, desired_lo, &res)) {
        printf("Target LO: %u Hz\n", desired_lo);
        printf("Actual LO: %u Hz (RF_DIV=%u, INT=%u, FRAC=%u, MOD=%u)\n",
               res.actual_hz, res.rf_div, res.int_val, res.frac_val, res.mod_val);
    } else {
        printf("Error: Frequency out of range!\n");
    }
    return 0;
}
