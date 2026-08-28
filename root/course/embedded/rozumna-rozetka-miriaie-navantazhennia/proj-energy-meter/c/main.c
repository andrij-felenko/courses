#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HLW8032_FRAME_LEN       24
#define HLW8032_SYNC_BYTE1      0x55
#define HLW8032_SYNC_BYTE2      0x5A

/* Стани скінченного автомата розбору кадру UART */
typedef enum {
    STATE_WAIT_SYNC1 = 0,
    STATE_WAIT_SYNC2,
    STATE_COLLECT_DATA
} hlw8032_parser_state_t;

/* Структура результатів вимірювання мережі */
typedef struct {
    float voltage_rms;        /* Напруга, В (RMS) */
    float current_rms;        /* Струм, А (RMS) */
    float active_power;       /* Активна потужність, Вт */
    float apparent_power;     /* Повна потужність, ВА */
    float power_factor;       /* Коефіцієнт потужності (0.00...1.00) */
    uint64_t energy_micro_ws; /* Накопичена енергія у мікро-ват-секундах (мкДж) */
    double energy_kwh;        /* Накопичена енергія, кВт·год */
    uint32_t valid_frames;    /* Лічильник успішно прийнятих кадрів */
    uint32_t checksum_errors; /* Лічильник помилок контрольної суми */
} energy_metrics_t;

/* Контекст драйвера енергомонітора */
typedef struct {
    hlw8032_parser_state_t state;
    uint8_t buffer[HLW8032_FRAME_LEN];
    uint8_t byte_idx;
    float k_voltage;          /* Калібрувальний коефіцієнт напруги (типово ~1.881) */
    float k_current;          /* Калібрувальний коефіцієнт струму (типово ~1.000) */
    energy_metrics_t metrics;
} hlw8032_driver_t;

/* Ініціалізація драйвера з калібрувальними коефіцієнтами */
void hlw8032_init(hlw8032_driver_t *drv, float k_v, float k_i) {
    if (!drv) return;
    memset(drv, 0, sizeof(hlw8032_driver_t));
    drv->state = STATE_WAIT_SYNC1;
    drv->k_voltage = (k_v > 0.0f) ? k_v : 1.881f;
    drv->k_current = (k_i > 0.0f) ? k_i : 1.000f;
}

/* Допоміжна функція складання 24-бітного числа з Big-Endian байтів */
static inline uint32_t unpack_u24(const uint8_t *p) {
    return ((uint32_t)p[0] << 16) | ((uint32_t)p[1] << 8) | (uint32_t)p[2];
}

/* Обробка повністю зібраного валідного кадру */
static void hlw8032_process_frame(hlw8032_driver_t *drv) {
    const uint8_t *buf = drv->buffer;

    /* Перевірка контрольної суми: сума байтів від 2 до 22 modulo 256 */
    uint8_t sum = 0;
    for (int i = 2; i <= 22; i++) {
        sum += buf[i];
    }

    if (sum != buf[23]) {
        drv->metrics.checksum_errors++;
        return;
    }

    drv->metrics.valid_frames++;

    /* Декодування 24-бітних регістрів */
    uint32_t v_param = unpack_u24(&buf[2]);
    uint32_t v_data  = unpack_u24(&buf[5]);
    uint32_t i_param = unpack_u24(&buf[8]);
    uint32_t i_data  = unpack_u24(&buf[11]);
    uint32_t p_param = unpack_u24(&buf[14]);
    uint32_t p_data  = unpack_u24(&buf[17]);

    /* Розрахунок напруги V_rms */
    if (v_data > 0) {
        drv->metrics.voltage_rms = ((float)v_param / (float)v_data) * drv->k_voltage;
    }

    /* Розрахунок струму I_rms (з відсіканням шуму при нульовому навантаженні) */
    if (i_data > 0) {
        float raw_current = ((float)i_param / (float)i_data) * drv->k_current;
        drv->metrics.current_rms = (raw_current >= 0.015f) ? raw_current : 0.0f;
    } else {
        drv->metrics.current_rms = 0.0f;
    }

    /* Розрахунок активної потужності P_active */
    if (p_data > 0 && drv->metrics.current_rms > 0.0f) {
        drv->metrics.active_power = ((float)p_param / (float)p_data) * drv->k_voltage * drv->k_current;
    } else {
        drv->metrics.active_power = 0.0f;
    }

    /* Розрахунок повної потужності S та коефіцієнта потужності PF */
    drv->metrics.apparent_power = drv->metrics.voltage_rms * drv->metrics.current_rms;
    if (drv->metrics.apparent_power > 0.1f) {
        float pf = drv->metrics.active_power / drv->metrics.apparent_power;
        drv->metrics.power_factor = (pf > 1.0f) ? 1.0f : ((pf < 0.0f) ? 0.0f : pf);
    } else {
        drv->metrics.power_factor = 1.0f;
    }

    /* Інтегрування енергії: кадр надходить кожні 50 мс (0.05 с).
     * Енергія за кадр = P * 0.05 с.
     * У мікро-ват-секундах: P * 50000 мкВт·с */
    uint64_t delta_uWs = (uint64_t)(drv->metrics.active_power * 50000.0f);
    drv->metrics.energy_micro_ws += delta_uWs;

    /* 1 кВт·год = 3.6e12 мкВт·с (3.6e9 Дж = 3.6e6 Вт·год) */
    drv->metrics.energy_kwh = (double)drv->metrics.energy_micro_ws / 3.6e12;
}

/* Побайтний парсер вхідного потоку UART (викликається в ISR або потоці зчитування) */
void hlw8032_feed_byte(hlw8032_driver_t *drv, uint8_t byte) {
    if (!drv) return;

    switch (drv->state) {
    case STATE_WAIT_SYNC1:
        if (byte == HLW8032_SYNC_BYTE1) {
            drv->buffer[0] = byte;
            drv->state = STATE_WAIT_SYNC2;
        }
        break;

    case STATE_WAIT_SYNC2:
        if (byte == HLW8032_SYNC_BYTE2) {
            drv->buffer[1] = byte;
            drv->byte_idx = 2;
            drv->state = STATE_COLLECT_DATA;
        } else if (byte == HLW8032_SYNC_BYTE1) {
            drv->buffer[0] = byte;
        } else {
            drv->state = STATE_WAIT_SYNC1;
        }
        break;

    case STATE_COLLECT_DATA:
        drv->buffer[drv->byte_idx++] = byte;
        if (drv->byte_idx >= HLW8032_FRAME_LEN) {
            hlw8032_process_frame(drv);
            drv->state = STATE_WAIT_SYNC1;
        }
        break;
    }
}
