/* power_governor.h - Адаптивний менеджер живлення сонячного вузла (C99) */
#ifndef POWER_GOVERNOR_H
#define POWER_GOVERNOR_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    POWER_STATE_NORMAL = 0,    /* SoC > 70%: повна функціональність */
    POWER_STATE_ECO,           /* 30% < SoC <= 70%: пакетування, без GPS */
    POWER_STATE_SURVIVAL,      /* 10% < SoC <= 30%: лише маяк кожні 6-12 год */
    POWER_STATE_HIBERNATE,     /* SoC <= 10%: консервація, сон 24 год */
    POWER_STATE_RECOVERY       /* Очікування накопичення заряду після блекауту */
} power_state_t;

typedef struct {
    uint16_t v_normal_mv;      /* Поріг переходу в Normal (наприклад, 3350 мВ) */
    uint16_t v_eco_mv;         /* Поріг переходу в Eco (наприклад, 3250 мВ) */
    uint16_t v_survival_mv;    /* Поріг переходу в Survival (наприклад, 3100 мВ) */
    uint16_t v_hibernate_mv;   /* Поріг відсічки Hibernate (наприклад, 2900 мВ) */
    uint16_t v_recovery_mv;    /* Поріг виходу з блекауту (наприклад, 3400 мВ) */
    uint16_t v_hysteresis_mv;  /* Гістерезис зворотного переходу (наприклад, 50 мВ) */
    int8_t   temp_charge_min_c;/* Мінімальна температура заряду (0 °C для LiFePO4) */
    uint16_t soak_time_req_s;  /* Час стабільного заряду для виходу з блекауту (900 с) */
} power_config_t;

typedef struct {
    uint16_t voltage_mv;       /* Поточна напруга акумулятора (мВ) */
    int8_t   temp_celsius;     /* Поточна температура батареї (°C) */
    uint16_t charge_current_ma;/* Струм заряджання від сонячної панелі (мА) */
} power_telemetry_t;

typedef struct {
    power_state_t  current_state;
    power_config_t config;
    uint32_t       soak_counter_s;
    bool           charge_enabled;
    bool           sensors_enabled;
    bool           radio_enabled;
} power_governor_t;

void power_governor_init(power_governor_t *gov, const power_config_t *cfg);
void power_governor_update(power_governor_t *gov, const power_telemetry_t *telem, uint32_t elapsed_s);
uint32_t power_governor_get_sleep_seconds(const power_governor_t *gov);

#ifdef __cplusplus
}
#endif

#endif /* POWER_GOVERNOR_H */
