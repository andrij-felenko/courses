#ifndef HYSTERESIS_CONTROLLER_H
#define HYSTERESIS_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

#define HYST_MEDIAN_WINDOW 5

typedef enum {
    HYST_MODE_ACTIVE_LOW  = 0, /* Нагрівання: УВІМК при <= Low, ВИМК при >= High */
    HYST_MODE_ACTIVE_HIGH = 1  /* Охолодження: УВІМК при >= High, ВИМК при <= Low */
} hyst_mode_t;

typedef struct {
    float threshold_low;       /* Нижній поріг перемикання */
    float threshold_high;      /* Верхній поріг перемикання */
    uint32_t min_on_time_ms;   /* Мінімальний час увімкненого стану */
    uint32_t min_off_time_ms;  /* Мінімальний час вимкненого стану */
    float ema_alpha;           /* Коефіцієнт фільтра EMA (0.0 < alpha <= 1.0) */
    hyst_mode_t mode;          /* Режим: нагрівання або охолодження */
} hyst_config_t;

typedef struct {
    float median_buf[HYST_MEDIAN_WINDOW];
    uint8_t median_idx;
    uint8_t median_count;
    float ema_val;
    bool ema_initialized;
    bool current_state;        /* Поточний стан виходу (true = ON, false = OFF) */
    uint32_t last_switch_ms;   /* Часова мітка останнього перемикання */
} hyst_state_t;

typedef struct {
    hyst_config_t cfg;
    hyst_state_t  state;
} hyst_controller_t;

/* Ініціалізація структури контролера */
void hyst_init(hyst_controller_t *ctrl, const hyst_config_t *cfg, uint32_t now_ms);

/* Оновлення стану контролера новим сирим вимірюванням датчика */
bool hyst_update(hyst_controller_t *ctrl, float raw_sample, uint32_t now_ms);

/* Отримання поточного стану виходу */
bool hyst_get_state(const hyst_controller_t *ctrl);

/* Отримання відфільтрованого значення сигналу */
float hyst_get_filtered_value(const hyst_controller_t *ctrl);

#endif /* HYSTERESIS_CONTROLLER_H */
