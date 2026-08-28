#include <stdint.h>
#include <stdbool.h>

#define DSHOT_DISARM_VALUE        0
#define DSHOT_MIN_THROTTLE        48
#define DSHOT_MAX_THROTTLE        2047
#define DSHOT_DMA_BUFFER_SIZE     17

typedef struct {
    uint32_t timer_arr;        /* Значення Auto-Reload Register таймера */
    uint32_t ccr_bit0;         /* Поріг компаратора для логічного 0 (33% ARR) */
    uint32_t ccr_bit1;         /* Поріг компаратора для логічного 1 (67% ARR) */
    uint8_t motor_pole_pairs;  /* Кількість пар полюсів ротора (типово 7 для 14P) */
    bool bidirectional;        /* true = інвертований CRC для Bi-dir DShot */
} dshot_config_t;

typedef struct {
    bool valid;
    uint32_t erpm;
    uint32_t rpm;
    uint8_t raw_type;
    uint8_t raw_payload;
} dshot_telemetry_t;

/* Таблиця декодування 5b4b GCR (32 елементи для швидкого індексування) */
static const int8_t gcr_decode_table[32] = {
    -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,  /* 0x00 - 0x07 */
    -1,   -1,   -1,   -1,   -1, 0x0D, 0x0E, 0x0F,  /* 0x08 - 0x0F: 13, 14, 15 */
    -1,   -1, 0x08, 0x09,   -1, 0x05, 0x0A, 0x0B,  /* 0x10 - 0x17: 8, 9, 5, 10, 11 */
    -1, 0x00, 0x0C, 0x01,   -1, 0x04, 0x02, 0x03   /* 0x18 - 0x1F: 0, 12, 1, 4, 2, 3 */
};

/* Ініціалізація структури конфігурації */
void dshot_init(dshot_config_t *cfg, uint32_t timer_arr, uint8_t pole_pairs, bool bidir) {
    cfg->timer_arr = timer_arr;
    cfg->ccr_bit0 = (timer_arr * 33) / 100;
    cfg->ccr_bit1 = (timer_arr * 67) / 100;
    cfg->motor_pole_pairs = (pole_pairs > 0) ? pole_pairs : 7;
    cfg->bidirectional = bidir;
}

/* Формування 16-бітного пакета DShot */
uint16_t dshot_create_packet(uint16_t throttle, bool request_tlm, bool bidirectional) {
    if (throttle > DSHOT_MAX_THROTTLE) {
        throttle = DSHOT_MAX_THROTTLE;
    }

    uint16_t packet = (throttle << 1) | (request_tlm ? 1 : 0);
    uint16_t csum = 0;
    uint16_t csum_data = packet;

    /* 4-бітний XOR трьох ніблів */
    for (int i = 0; i < 3; i++) {
        csum ^= (csum_data & 0x0F);
        csum_data >>= 4;
    }

    if (bidirectional) {
        csum = (~csum) & 0x0F;
    } else {
        csum &= 0x0F;
    }

    return (packet << 4) | csum;
}

/* Заповнення буфера DMA значеннями CCR для таймера */
void dshot_fill_dma_buffer(const dshot_config_t *cfg, uint16_t packet, uint32_t *dma_buf) {
    for (int i = 0; i < 16; i++) {
        /* Старший біт іде першим (MSB first) */
        if (packet & (1 << (15 - i))) {
            dma_buf[i] = cfg->ccr_bit1;
        } else {
            dma_buf[i] = cfg->ccr_bit0;
        }
    }
    /* Завершальний рівень для міжкадрової паузи */
    dma_buf[16] = 0;
}

/* Декодування 20/21-бітного GCR потоку телеметрії */
bool dshot_decode_telemetry(const dshot_config_t *cfg, uint32_t raw_gcr, dshot_telemetry_t *out) {
    out->valid = false;
    out->erpm = 0;
    out->rpm = 0;

    /* Виділяємо чотири 5-бітні GCR символи (20 бітів) */
    uint8_t gcr3 = (raw_gcr >> 15) & 0x1F;
    uint8_t gcr2 = (raw_gcr >> 10) & 0x1F;
    uint8_t gcr1 = (raw_gcr >> 5)  & 0x1F;
    uint8_t gcr0 = (raw_gcr >> 0)  & 0x1F;

    int8_t nib3 = gcr_decode_table[gcr3];
    int8_t nib2 = gcr_decode_table[gcr2];
    int8_t nib1 = gcr_decode_table[gcr1];
    int8_t nib0 = gcr_decode_table[gcr0];

    if (nib3 < 0 || nib2 < 0 || nib1 < 0 || nib0 < 0) {
        return false; /* Помилка GCR-символу */
    }

    uint16_t value_12bit = ((uint16_t)nib3 << 8) | ((uint16_t)nib2 << 4) | (uint16_t)nib1;
    uint8_t received_crc = (uint8_t)nib0;

    /* Перевірка контрольної суми відповіді телеметрії */
    uint8_t calc_crc = (~(value_12bit ^ (value_12bit >> 4) ^ (value_12bit >> 8))) & 0x0F;
    if (calc_crc != received_crc) {
        return false; /* Помилка контрольної суми */
    }

    out->valid = true;
    out->raw_type = (value_12bit >> 8) & 0x0F;
    out->raw_payload = value_12bit & 0xFF;

    /* Розпакування періоду ERPM (експонента E = 3 біти, мантиса M = 9 бітів) */
    uint8_t exponent = (value_12bit >> 9) & 0x07;
    uint16_t mantissa = value_12bit & 0x01FF;

    if (mantissa == 0) {
        out->erpm = 0;
        out->rpm = 0;
        return true;
    }

    /* Період комутації в мікросекундах */
    uint32_t period_us = (uint32_t)mantissa << exponent;
    if (period_us == 0) {
        return true;
    }

    /* ERPM = (1000000 мкс / T_comm) * (60 сек / 6 кроків) = 10000000 / period_us */
    out->erpm = 10000000UL / period_us;
    out->rpm = out->erpm / cfg->motor_pole_pairs;

    return true;
}
