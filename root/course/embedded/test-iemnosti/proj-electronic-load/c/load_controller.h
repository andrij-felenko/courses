/* load_controller.h - C implementation */
#ifndef LOAD_CONTROLLER_H
#define LOAD_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    MODE_CC = 0,    /* Постійний струм (мА) */
    MODE_CR,        /* Постійний опір (мОм) */
    MODE_CP,        /* Постійна потужність (мВт) */
    MODE_PULSED     /* Імпульсний профіль (радіотракт) */
} load_mode_t;

typedef enum {
    STATE_IDLE = 0,
    STATE_RUNNING,
    STATE_IR_STEP,
    STATE_CUTOFF_REACHED,
    STATE_OVERHEAT_FAULT
} load_state_t;

typedef struct {
    load_mode_t mode;
    uint32_t setpoint_val;     /* мА для CC, мОм для CR, мВт для CP */
    uint32_t pulse_high_ma;    /* Струм імпульсу для Pulsed (мА) */
    uint32_t pulse_low_ma;     /* Струм бази для Pulsed (мА) */
    uint32_t pulse_high_ms;    /* Тривалість імпульсу (мс) */
    uint32_t pulse_period_ms;  /* Період повторення (мс) */
    uint32_t cutoff_mv;        /* Кінцева напруга відсічки (мВ) */
    uint32_t max_temp_c;       /* Максимальна температура радіатора (°C) */
} load_config_t;

typedef struct {
    load_state_t state;
    load_config_t cfg;
    uint32_t v_cell_mv;        /* Поточна напруга комірки (мВ) */
    uint32_t i_actual_ma;      /* Фактичний струм (мА) */
    uint32_t temp_heatsink_c;  /* Температура радіатора (°C) */
    
    /* Інтегратори */
    uint64_t microamp_seconds; /* Кулонометрія (мкА·с) */
    uint64_t microwatt_seconds;/* Лічильник енергії (мкВт·с) */
    
    /* Розрахунок DC IR */
    uint32_t ir_v_baseline_mv;
    uint32_t ir_i_baseline_ma;
    uint32_t last_dc_ir_mohm;
    uint32_t ir_timer_ms;
    
    uint32_t elapsed_ms;
} load_tester_t;

/* HAL-колбеки для зв'язку з апаратним рівнем */
typedef struct {
    void (*set_dac_current_ma)(uint32_t ma);
    void (*read_adc_channels)(uint32_t *v_cell_mv, uint32_t *i_shunt_ma, uint32_t *temp_c);
    void (*send_uart_log)(const char *str);
} load_hal_t;

void load_tester_init(load_tester_t *t, const load_config_t *cfg, const load_hal_t *hal);
void load_tester_start(load_tester_t *t);
void load_tester_stop(load_tester_t *t);
void load_tester_tick(load_tester_t *t, uint32_t dt_ms);

#endif /* LOAD_CONTROLLER_H */
