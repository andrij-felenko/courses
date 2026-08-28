#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Коди помилок розрахунку ToA */
typedef enum {
    TOA_OK = 0,
    TOA_ERR_INVALID_SF = -1,
    TOA_ERR_INVALID_BW = -2,
    TOA_ERR_INVALID_CR = -3,
    TOA_ERR_PAYLOAD_TOO_LARGE = -4
} toa_status_t;

/* Конфігурація кадра LoRa */
typedef struct {
    uint8_t sf;              /* Spreading Factor: 7..12 */
    uint32_t bw_hz;          /* Bandwidth в Гц: 125000, 250000, 500000 */
    uint8_t cr;              /* Coding Rate: 1 (4/5), 2 (4/6), 3 (4/7), 4 (4/8) */
    uint16_t preamble_syms;  /* Кількість символів преамбули (типово 8) */
    bool header_explicit;    /* true = Explicit Header, false = Implicit Header */
    bool crc_on;             /* true = CRC увімкнено */
    bool ldro_auto;          /* true = автоматичне увімкнення LDRO при T_s > 16 мс */
} lora_config_t;

/* Результат розрахунку часу */
typedef struct {
    uint32_t toa_us;         /* Час в ефірі в мікросекундах */
    uint32_t off_time_us;    /* Необхідна пауза мовчання при 1% Duty Cycle */
    uint16_t payload_syms;   /* Кількість символів корисного навантаження */
} toa_result_t;

/**
 * @brief Обчислює час в ефірі та паузу мовчання для пакета LoRa
 */
toa_status_t lora_calculate_toa(const lora_config_t *cfg, uint8_t payload_bytes, toa_result_t *res) {
    if (!cfg || !res) return TOA_ERR_INVALID_BW;
    if (cfg->sf < 7 || cfg->sf > 12) return TOA_ERR_INVALID_SF;
    if (cfg->bw_hz == 0) return TOA_ERR_INVALID_BW;
    if (cfg->cr < 1 || cfg->cr > 4) return TOA_ERR_INVALID_CR;
    if (payload_bytes > 255) return TOA_ERR_PAYLOAD_TOO_LARGE;

    /* 1. Тривалість одного символа у мікросекундах: T_s = (2^SF / BW) * 1000000 */
    double t_s_us = ((double)(1UL << cfg->sf) / (double)cfg->bw_hz) * 1000000.0;

    /* 2. Автоматична або примусова оптимізація низької швидкості (LDRO) */
    bool use_ldro = cfg->ldro_auto && (t_s_us > 16000.0);
    uint8_t de_bit = use_ldro ? 1 : 0;

    /* 3. Тривалість преамбули: (N_pre + 4.25) * T_s */
    double t_preamble_us = ((double)cfg->preamble_syms + 4.25) * t_s_us;

    /* 4. Обчислення чисельника для кількості символів корисного навантаження */
    int32_t bits_num = 8 * payload_bytes - 4 * cfg->sf + 28 + (cfg->crc_on ? 16 : 0) - (cfg->header_explicit ? 0 : 20);
    if (bits_num < 0) {
        bits_num = 0;
    }

    int32_t bits_den = 4 * (cfg->sf - 2 * de_bit);
    uint16_t blocks = (uint16_t)ceil((double)bits_num / (double)bits_den);

    uint16_t n_payload = 8 + blocks * (cfg->cr + 4);
    double t_payload_us = (double)n_payload * t_s_us;

    /* 5. Підсумковий час в ефірі */
    double total_toa_us = t_preamble_us + t_payload_us;

    res->toa_us = (uint32_t)ceil(total_toa_us);
    res->payload_syms = n_payload;
    /* Пауза мовчання при 1% Duty Cycle: t_off = ToA * 99 */
    res->off_time_us = res->toa_us * 99U;

    return TOA_OK;
}

int main(void) {
    lora_config_t cfg = {
        .sf = 7,
        .bw_hz = 125000,
        .cr = 1,
        .preamble_syms = 8,
        .header_explicit = true,
        .crc_on = true,
        .ldro_auto = true
    };

    toa_result_t res;
    toa_status_t status = lora_calculate_toa(&cfg, 20, &res);

    if (status == TOA_OK) {
        printf("SF7, BW 125 kHz, Payload 20 bytes:\n");
        printf("  ToA: %lu us (%.2f ms)\n", (unsigned long)res.toa_us, res.toa_us / 1000.0);
        printf("  Off-Time (1%% DC): %lu us (%.2f s)\n", (unsigned long)res.off_time_us, res.off_time_us / 1000000.0);
        printf("  Payload symbols: %u\n", res.payload_syms);
    } else {
        printf("Помилка розрахунку: %d\n", status);
    }

    return 0;
}
