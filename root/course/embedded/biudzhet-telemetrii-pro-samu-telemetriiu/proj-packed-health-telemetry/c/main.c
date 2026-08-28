#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Причини останнього апаратного або програмного скидання */
typedef enum {
    RESET_CAUSE_POR        = 0, /* Power-On Reset */
    RESET_CAUSE_WDT        = 1, /* Watchdog Timer Timeout */
    RESET_CAUSE_BOR        = 2, /* Brown-Out Reset (провал живлення) */
    RESET_CAUSE_SOFT       = 3, /* Програмне скидання (NVIC_SystemReset) */
    RESET_CAUSE_HARDFAULT  = 4, /* Помилка виконання HardFault / Lockup */
    RESET_CAUSE_PIN        = 5  /* Зовнішній пін NRST */
} reset_cause_t;

/* Вхідна структура сирих метрик здоров'я */
typedef struct {
    reset_cause_t reset_cause;
    bool          low_batt_flag;
    bool          radio_retry_flag;
    bool          flash_error_flag;
    bool          sensor_error_flag;
    bool          tamper_flag;
    uint16_t      v_batt_mv;        /* Напруга під навантаженням, мВ */
    uint16_t      v_sag_mv;         /* Просадка напруги (V_oc - V_load), мВ */
    int8_t        rssi_dbm;         /* Рівень сигналу, dBm (-120..-57) */
    uint8_t       tx_retries;       /* Кількість повторних відправок (0..3+) */
    uint32_t      min_free_heap;    /* Мінімальний залишок купи, байти */
    int8_t        mcu_temp_c;       /* Температура чипа, °C (-40..+87) */
    uint32_t      uptime_hours;     /* Час роботи, години */
} health_metrics_t;

/* Режими роботи діагностичного планувальника */
typedef enum {
    DIAG_MODE_PIGGYBACK_ONLY = 0, /* Звичайний режим: 1 статус-байт до даних */
    DIAG_MODE_FULL_HEARTBEAT = 1, /* Плановий повний кадр (раз на 6-24 год) */
    DIAG_MODE_BURST_ANOMALY  = 2  /* Аварійний сплеск при виявленні деградації */
} diag_schedule_mode_t;

/* Упаковка 8-байтового діагностичного кадру без побітових структур (безпечно до Endianness) */
void pack_health_frame(const health_metrics_t *in, uint8_t out[8]) {
    /* Байт 0: Прапорці та причина перезавантаження */
    uint8_t b0 = ((uint8_t)(in->reset_cause & 0x07) << 5);
    if (in->low_batt_flag)     b0 |= (1U << 4);
    if (in->radio_retry_flag)  b0 |= (1U << 3);
    if (in->flash_error_flag)  b0 |= (1U << 2);
    if (in->sensor_error_flag) b0 |= (1U << 1);
    if (in->tamper_flag)       b0 |= (1U << 0);
    out[0] = b0;

    /* Байт 1: Напруга батареї (2000..4550 мВ -> 0..255, крок 10 мВ) */
    uint16_t v = in->v_batt_mv;
    if (v < 2000) v = 2000;
    if (v > 4550) v = 4550;
    out[1] = (uint8_t)((v - 2000) / 10);

    /* Байт 2: Просадка напруги (0..510 мВ -> 0..255, крок 2 мВ) */
    uint16_t sag = in->v_sag_mv;
    if (sag > 510) sag = 510;
    out[2] = (uint8_t)(sag / 2);

    /* Байт 3: RSSI (-120..-57 -> 0..63) [6 бітів] + Retries (0..3) [2 біти] */
    int8_t r = in->rssi_dbm;
    if (r < -120) r = -120;
    if (r > -57)  r = -57;
    uint8_t rssi_encoded = (uint8_t)(r + 120); /* 0..63 */
    uint8_t retries = in->tx_retries > 3 ? 3 : in->tx_retries;
    out[3] = (uint8_t)((rssi_encoded << 2) | (retries & 0x03));

    /* Байт 4: Мінімум вільної купи (0..65280 байтів, квант 256 байтів) */
    uint32_t heap_q = in->min_free_heap / 256;
    out[4] = (uint8_t)(heap_q > 255 ? 255 : heap_q);

    /* Байт 5: Температура MCU (-40..+87 °C, зміщення +40 -> 0..127) */
    int8_t temp = in->mcu_temp_c;
    if (temp < -40) temp = -40;
    if (temp > 87)  temp = 87;
    out[5] = (uint8_t)(temp + 40);

    /* Байт 6-7: Аптайм у годинах (uint16_t Little-Endian) */
    uint16_t up = (uint16_t)(in->uptime_hours > 65535 ? 65535 : in->uptime_hours);
    out[6] = (uint8_t)(up & 0xFF);
    out[7] = (uint8_t)((up >> 8) & 0xFF);
}

/* Розпаковка 8-байтового кадру на боці сервера */
void unpack_health_frame(const uint8_t in[8], health_metrics_t *out) {
    /* Байт 0 */
    out->reset_cause       = (reset_cause_t)((in[0] >> 5) & 0x07);
    out->low_batt_flag     = (in[0] & (1U << 4)) != 0;
    out->radio_retry_flag  = (in[0] & (1U << 3)) != 0;
    out->flash_error_flag  = (in[0] & (1U << 2)) != 0;
    out->sensor_error_flag = (in[0] & (1U << 1)) != 0;
    out->tamper_flag       = (in[0] & (1U << 0)) != 0;

    /* Байт 1 */
    out->v_batt_mv = (uint16_t)(in[1] * 10 + 2000);

    /* Байт 2 */
    out->v_sag_mv = (uint16_t)(in[2] * 2);

    /* Байт 3 */
    out->rssi_dbm   = (int8_t)((in[3] >> 2) - 120);
    out->tx_retries = in[3] & 0x03;

    /* Байт 4 */
    out->min_free_heap = (uint32_t)(in[4] * 256);

    /* Байт 5 */
    out->mcu_temp_c = (int8_t)(in[5] - 40);

    /* Байт 6-7 */
    out->uptime_hours = (uint32_t)(in[6] | (in[7] << 8));
}

/* Генерація 1 статус-байта для регулярного підсаджування (Piggybacking) */
uint8_t generate_piggyback_status(const health_metrics_t *in) {
    uint8_t status = 0;
    if (in->low_batt_flag || in->v_batt_mv < 3000) status |= (1U << 7);
    if (in->v_sag_mv > 350)                        status |= (1U << 6);
    if (in->radio_retry_flag || in->tx_retries > 2) status |= (1U << 5);
    if (in->flash_error_flag)                      status |= (1U << 4);
    if (in->sensor_error_flag)                     status |= (1U << 3);
    if (in->min_free_heap < 1024)                  status |= (1U << 2);
    return status;
}

/* Оцінка стану та вибір режиму планувальника */
diag_schedule_mode_t evaluate_diag_scheduler(const health_metrics_t *m, uint32_t cycles_since_full) {
    /* Тригери аварійного сплеску (Anomaly Burst) */
    if (m->v_sag_mv > 400 || m->v_batt_mv < 2900 || m->tx_retries >= 3 || m->min_free_heap < 512) {
        return DIAG_MODE_BURST_ANOMALY;
    }

    /* Плановий пульс кожні 36 циклів (раз на 6 годин при 10-хвилинному кроці) */
    if (cycles_since_full >= 36) {
        return DIAG_MODE_FULL_HEARTBEAT;
    }

    return DIAG_MODE_PIGGYBACK_ONLY;
}
