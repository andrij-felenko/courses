/* Конфігурація часових параметрів I2C за специфікацією NXP UM10204 (C11) */
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    I2C_MODE_STANDARD_100K = 0,
    I2C_MODE_FAST_400K     = 1,
    I2C_MODE_FAST_PLUS_1M  = 2,
    I2C_MODE_HIGH_SPEED_3M4 = 3
} i2c_speed_mode_t;

typedef struct {
    uint32_t scl_freq_hz;     /* Бажана тактова частота SCL у Гц */
    uint16_t t_low_ns;        /* Тривалість низького рівня SCL у нс */
    uint16_t t_high_ns;       /* Тривалість високого рівня SCL у нс */
    uint16_t t_su_dat_ns;     /* Час встановлення даних у нс */
    uint16_t t_hd_dat_ns;     /* Час утримання даних у нс */
    uint16_t t_su_sta_ns;     /* Час встановлення Repeated START у нс */
    uint16_t t_hd_sta_ns;     /* Час утримання START у нс */
    uint16_t t_su_sto_ns;     /* Час встановлення STOP у нс */
    uint16_t t_buf_ns;        /* Вільний час шини між транзакціями у нс */
    uint16_t t_r_max_ns;      /* Очікуваний максимальний час наростання */
    uint16_t t_f_max_ns;      /* Очікуваний максимальний час спаду */
    uint8_t  digital_filter_clocks; /* Фільтр сплесків t_SP (0...15 тактів ядра) */
} i2c_timing_spec_t;

/* Нормативні табличні значення за NXP UM10204 */
static const i2c_timing_spec_t I2C_TIMINGS_STANDARD = {
    .scl_freq_hz = 100000,
    .t_low_ns    = 4700,
    .t_high_ns   = 4000,
    .t_su_dat_ns = 250,
    .t_hd_dat_ns = 300,
    .t_su_sta_ns = 4700,
    .t_hd_sta_ns = 4000,
    .t_su_sto_ns = 4000,
    .t_buf_ns    = 4700,
    .t_r_max_ns  = 1000,
    .t_f_max_ns  = 300,
    .digital_filter_clocks = 0
};

static const i2c_timing_spec_t I2C_TIMINGS_FAST = {
    .scl_freq_hz = 400000,
    .t_low_ns    = 1300,
    .t_high_ns   = 600,
    .t_su_dat_ns = 100,
    .t_hd_dat_ns = 300,
    .t_su_sta_ns = 600,
    .t_hd_sta_ns = 600,
    .t_su_sto_ns = 600,
    .t_buf_ns    = 1300,
    .t_r_max_ns  = 300,
    .t_f_max_ns  = 300,
    .digital_filter_clocks = 2
};

static const i2c_timing_spec_t I2C_TIMINGS_FAST_PLUS = {
    .scl_freq_hz = 1000000,
    .t_low_ns    = 500,
    .t_high_ns   = 260,
    .t_su_dat_ns = 50,
    .t_hd_dat_ns = 0,
    .t_su_sta_ns = 260,
    .t_hd_sta_ns = 260,
    .t_su_sto_ns = 260,
    .t_buf_ns    = 500,
    .t_r_max_ns  = 120,
    .t_f_max_ns  = 120,
    .digital_filter_clocks = 1
};
