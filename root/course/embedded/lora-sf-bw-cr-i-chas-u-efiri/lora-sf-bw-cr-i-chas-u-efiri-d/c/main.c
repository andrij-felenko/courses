#include <stdint.h>
#include <stdbool.h>

/* Переліки параметрів фізичного рівня LoRa */
typedef enum {
    LORA_SF5  = 5,
    LORA_SF6  = 6,
    LORA_SF7  = 7,
    LORA_SF8  = 8,
    LORA_SF9  = 9,
    LORA_SF10 = 10,
    LORA_SF11 = 11,
    LORA_SF12 = 12
} lora_sf_t;

typedef enum {
    LORA_BW_125_KHZ = 125000,
    LORA_BW_250_KHZ = 250000,
    LORA_BW_500_KHZ = 500000
} lora_bw_t;

typedef enum {
    LORA_CR_4_5 = 1,
    LORA_CR_4_6 = 2,
    LORA_CR_4_7 = 3,
    LORA_CR_4_8 = 4
} lora_cr_t;

typedef struct {
    lora_sf_t sf;
    lora_bw_t bw;
    lora_cr_t cr;
    uint16_t  preamble_len;  /* Зазвичай 8 символів */
    bool      explicit_header;
    bool      crc_enabled;
    bool      low_data_rate_opt;
} lora_config_t;

/*
 * Точний розрахунок тривалості передачі пакета (Time-on-Air) в мікросекундах.
 * Реалізовано за специфікацією Semtech з оптимізацією для цілочисельної арифметики.
 */
uint32_t lora_calc_toa_us(const lora_config_t *cfg, uint8_t payload_len) {
    if (!cfg) return 0;

    /* 1. Тривалість одного символу Ts в мікросекундах: Ts_us = (2^SF * 1000000) / BW */
    uint32_t n_chips = (uint32_t)1 << cfg->sf;
    uint32_t ts_us = (uint32_t)(((uint64_t)n_chips * 1000000ULL) / cfg->bw);

    /* 2. Тривалість преамбули: T_preamble = (N_preamble + 4.25) * Ts */
    /* Множимо на 4 для цілочисельного представлення: 4.25 = 17/4 */
    uint32_t n_pream_x4 = ((uint32_t)cfg->preamble_len * 4) + 17;
    uint32_t t_preamble_us = (uint32_t)(((uint64_t)n_pream_x4 * ts_us) / 4);

    /* 3. Розрахунок кількості символів корисного навантаження */
    int32_t h_val = cfg->explicit_header ? 0 : 1;
    int32_t crc_val = cfg->crc_enabled ? 1 : 0;
    
    /* Автоматичне визначення LDRO (Low Data Rate Optimization), якщо символ > 16.38 мс */
    bool de_opt = cfg->low_data_rate_opt;
    if (ts_us > 16380) {
        de_opt = true;
    }
    int32_t de_val = de_opt ? 1 : 0;

    /* Чисельник: 8*PL - 4*SF + 28 + 16*CRC - 20*H */
    int32_t num = 8 * (int32_t)payload_len - 4 * (int32_t)cfg->sf + 28 + 16 * crc_val - 20 * h_val;
    /* Знаменник: 4 * (SF - 2*DE) */
    int32_t den = 4 * ((int32_t)cfg->sf - 2 * de_val);

    int32_t n_payload_sym = 8;
    if (num > 0 && den > 0) {
        /* Заокруглення вгору: ceil(num / den) = (num + den - 1) / den */
        int32_t ceil_val = (num + den - 1) / den;
        n_payload_sym += ceil_val * ((int32_t)cfg->cr + 4);
    }

    uint32_t t_payload_us = (uint32_t)n_payload_sym * ts_us;
    return t_preamble_us + t_payload_us;
}

/*
 * Розрахунок мінімального обов'язкового часу мовчання (Time-off) в мілісекундах
 * для дотримання ліміту Duty Cycle (наприклад, duty_cycle_percent = 1.0f).
 */
uint32_t lora_calc_time_off_ms(uint32_t toa_us, float duty_cycle_percent) {
    if (duty_cycle_percent <= 0.0f || duty_cycle_percent >= 100.0f) return 0;
    
    float toa_ms = (float)toa_us / 1000.0f;
    float time_off_ms = toa_ms * ((100.0f / duty_cycle_percent) - 1.0f);
    return (uint32_t)(time_off_ms + 0.5f);
}

/*
 * Простий алгоритм вибору SF на основі виміряного SNR (вхідний SNR у дБ)
 */
lora_sf_t lora_select_optimal_sf(int8_t snr_db) {
    const int8_t margin_db = 10; /* Запас надійності */

    if (snr_db >= (-7 + margin_db))  return LORA_SF7;
    if (snr_db >= (-10 + margin_db)) return LORA_SF8;
    if (snr_db >= (-12 + margin_db)) return LORA_SF9;
    if (snr_db >= (-15 + margin_db)) return LORA_SF10;
    if (snr_db >= (-17 + margin_db)) return LORA_SF11;
    return LORA_SF12;
}
