#include <stdint.h>
#include <stdbool.h>

typedef enum {
    I2C_MODE_STANDARD = 0, /* 100 kHz */
    I2C_MODE_FAST     = 1, /* 400 kHz */
    I2C_MODE_FAST_PLUS= 2  /* 1 MHz   */
} i2c_speed_mode_t;

typedef struct {
    uint32_t pclk_hz;       /* Тактова частота периферії (наприклад, 48000000 для 48 МГц) */
    uint32_t target_scl_hz; /* Бажана швидкість SCL (наприклад, 400000) */
    uint32_t rise_time_ns;  /* Оцінений/виміряний час наростання tr (нс) */
    uint32_t fall_time_ns;  /* Оцінений/виміряний час спадання tf (нс) */
    uint32_t dnf_cycles;    /* Цифровий фільтр шуму (0..15 циклів) */
    bool     analog_filter; /* Увімкнення аналогового фільтра (зазвичай 50 нс) */
} i2c_bus_params_t;

typedef struct {
    uint8_t  presc;     /* Подільник частоти (0..15) */
    uint8_t  scll;      /* Лічильник низького рівня SCL (0..255) */
    uint8_t  sclh;      /* Лічильник високого рівня SCL (0..255) */
    uint8_t  sdadel;    /* Затримка утримання даних (0..15) */
    uint8_t  scldel;    /* Затримка встановлення даних (0..15) */
    uint32_t raw_value; /* Упакований регістр TIMINGR */
    uint32_t actual_hz; /* Фактично отримана частота SCL */
} i2c_timing_reg_t;

typedef struct {
    uint32_t t_low_min_ns;
    uint32_t t_high_min_ns;
    uint32_t t_sudat_min_ns;
    uint32_t t_hddat_max_ns;
    uint32_t tr_max_ns;
    uint32_t tf_max_ns;
} i2c_mode_spec_t;

static const i2c_mode_spec_t SPECS[3] = {
    [I2C_MODE_STANDARD]  = { 4700, 4000, 250, 3450, 1000, 300 },
    [I2C_MODE_FAST]      = { 1300,  600, 100,  900,  300, 300 },
    [I2C_MODE_FAST_PLUS] = {  500,  260,  50,  450,  120, 120 }
};

bool i2c_calculate_timings(const i2c_bus_params_t *params,
                           i2c_speed_mode_t mode,
                           i2c_timing_reg_t *out)
{
    if (!params || !out || params->pclk_hz == 0 || params->target_scl_hz == 0) {
        return false;
    }

    const i2c_mode_spec_t *spec = &SPECS[mode];
    uint32_t t_af_ns = params->analog_filter ? 50 : 0;
    uint32_t tr = params->rise_time_ns > 0 ? params->rise_time_ns : spec->tr_max_ns;
    uint32_t tf = params->fall_time_ns > 0 ? params->fall_time_ns : spec->tf_max_ns;

    /* Обчислення періоду квантування t_I2CCLK у наносекундах */
    double t_pclk_ns = 1000000000.0 / (double)params->pclk_hz;
    uint32_t target_period_ns = 1000000000U / params->target_scl_hz;

    /* Пошук мінімального валідного значення PRESC (0..15) */
    for (uint32_t presc = 0; presc <= 15; ++presc) {
        double t_presc_ns = (double)(presc + 1) * t_pclk_ns;

        /* Сумарна затримка внутрішніх фільтрів */
        double t_filter_ns = (double)t_af_ns + ((double)params->dnf_cycles * t_pclk_ns);

        /* Розрахунок мінімальних значень SCLL та SCLH */
        double scll_min = (spec->t_low_min_ns + tf - t_filter_ns) / t_presc_ns - 1.0;
        double sclh_min = (spec->t_high_min_ns + tr - t_filter_ns) / t_presc_ns - 1.0;

        uint32_t scll_val = scll_min > 0.0 ? (uint32_t)(scll_min + 0.999) : 0;
        uint32_t sclh_val = sclh_min > 0.0 ? (uint32_t)(sclh_min + 0.999) : 0;

        /* Розрахунок сумарного періоду при мінімальних лічильниках */
        double current_period_ns = ((double)(scll_val + 1) + (double)(sclh_val + 1)) * t_presc_ns + tr + tf;

        /* Якщо базовий період менший за цільовий, розподіляємо надлишок порівну */
        if (current_period_ns < (double)target_period_ns) {
            double extra_ns = (double)target_period_ns - current_period_ns;
            uint32_t extra_ticks = (uint32_t)(extra_ns / t_presc_ns);
            scll_val += (extra_ticks + 1) / 2;
            sclh_val += extra_ticks / 2;
        }

        /* Перевірка на переповнення 8-бітних полів */
        if (scll_val > 255 || sclh_val > 255) {
            continue; /* Переходимо до більшого дільника PRESC */
        }

        /* Розрахунок затримок SCLDEL та SDADEL */
        double scldel_min = (spec->t_sudat_min_ns + tr - t_filter_ns) / t_presc_ns - 1.0;
        double sdadel_min = (tf - t_filter_ns) / t_presc_ns - 1.0;

        uint32_t scldel_val = scldel_min > 0.0 ? (uint32_t)(scldel_min + 0.999) : 0;
        uint32_t sdadel_val = sdadel_min > 0.0 ? (uint32_t)(sdadel_min + 0.999) : 0;

        /* Перевірка на переповнення 4-бітних полів */
        if (scldel_val > 15 || sdadel_val > 15) {
            continue;
        }

        /* Знайдено оптимальну комбінацію */
        out->presc   = (uint8_t)presc;
        out->scll    = (uint8_t)scll_val;
        out->sclh    = (uint8_t)sclh_val;
        out->sdadel  = (uint8_t)sdadel_val;
        out->scldel  = (uint8_t)scldel_val;

        /* Пакування в апаратний формат 32-бітного регістру */
        out->raw_value = ((uint32_t)out->presc  << 28) |
                         ((uint32_t)out->scldel << 20) |
                         ((uint32_t)out->sdadel << 16) |
                         ((uint32_t)out->sclh   << 8)  |
                         ((uint32_t)out->scll   << 0);

        double actual_period = ((double)(out->scll + 1) + (double)(out->sclh + 1)) * t_presc_ns + tr + tf;
        out->actual_hz = (uint32_t)(1000000000.0 / actual_period);

        return true;
    }

    return false; /* Не знайдено валідного налаштування для вказаних обмежень */
}
