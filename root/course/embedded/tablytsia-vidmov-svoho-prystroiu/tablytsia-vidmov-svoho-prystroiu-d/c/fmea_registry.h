/* fmea_registry.h / fmea_registry.c — Реєстр відмов та диспетчер самодіагностики (C99) */
#ifndef FMEA_REGISTRY_H
#define FMEA_REGISTRY_H

#include <stdint.h>
#include <stdbool.h>

/* Рівні пріоритету дій за стандартом AIAG-VDA */
typedef enum {
    FMEA_AP_LOW = 0,
    FMEA_AP_MEDIUM,
    FMEA_AP_HIGH
} fmea_action_priority_t;

/* Ідентифікатори критичних режимів відмов */
typedef enum {
    FMEA_ID_PWR_SUPPLY = 0,
    FMEA_ID_VALVE_MOSFET,
    FMEA_ID_PRESSURE_SENSOR,
    FMEA_ID_I2C_BUS,
    FMEA_ID_FLASH_MEMORY,
    FMEA_ID_STACK_OVERFLOW,
    FMEA_ID_COUNT
} fmea_failure_id_t;

/* Опис одного режиму відмови в реєстрі (Flash) */
typedef struct {
    fmea_failure_id_t       id;
    const char*             name;
    uint8_t                 severity;
    uint8_t                 occurrence;
    uint8_t                 detection;
    fmea_action_priority_t  ap;
    bool (*diag_func)(void);            /* Функція перевірки справності */
    void (*recovery_func)(void);        /* Функція локального відновлення */
} fmea_record_t;

/* Динамічний стан відмови в оперативній пам'яті (RAM) */
typedef struct {
    uint32_t fail_count;
    uint32_t last_fail_timestamp_ms;
    bool     is_active;
} fmea_runtime_state_t;

/* Розрахунок Action Priority за шкалою AIAG-VDA */
fmea_action_priority_t fmea_calculate_ap(uint8_t s, uint8_t o, uint8_t d);

/* Ініціалізація та періодичний аудит усіх вузлів */
void fmea_init(void);
void fmea_run_diagnostics(uint32_t current_time_ms);
bool fmea_is_system_safe(void);

#endif /* FMEA_REGISTRY_H */

/* --- Реалізація --- */
#include <stddef.h>

static fmea_runtime_state_t g_fmea_state[FMEA_ID_COUNT];

/* Заглушки функцій діагностики конкретних вузлів */
static bool diag_check_power(void) {
    /* Перевірка стану супервізора напруги BOD */
    return true; /* Норма */
}

static bool diag_check_valve(void) {
    /* Зчитування струмового шунта при закритому ключі */
    return true; /* Норма */
}

static bool diag_check_pressure(void) {
    /* Перевірка мінімального струму петлі 4-20 мА (> 3.5 мА) */
    return true; /* Норма */
}

static bool diag_check_i2c(void) {
    /* Перевірка прапорця зайнятості шини та стану SDA */
    return true; /* Норма */
}

static void recover_i2c_bus(void) {
    /* Процедура 9 тактів SCL через GPIO bit-banging */
}

/* Статичний реєстр FMEA у Flash-пам'яті */
static const fmea_record_t g_fmea_registry[FMEA_ID_COUNT] = {
    [FMEA_ID_PWR_SUPPLY] = {
        .id = FMEA_ID_PWR_SUPPLY,
        .name = "DC-DC Power Bus",
        .severity = 10, .occurrence = 1, .detection = 2,
        .ap = FMEA_AP_MEDIUM,
        .diag_func = diag_check_power,
        .recovery_func = NULL
    },
    [FMEA_ID_VALVE_MOSFET] = {
        .id = FMEA_ID_VALVE_MOSFET,
        .name = "Valve MOSFET Switch",
        .severity = 9, .occurrence = 1, .detection = 2,
        .ap = FMEA_AP_MEDIUM,
        .diag_func = diag_check_valve,
        .recovery_func = NULL
    },
    [FMEA_ID_PRESSURE_SENSOR] = {
        .id = FMEA_ID_PRESSURE_SENSOR,
        .name = "Pressure Loop 4-20mA",
        .severity = 8, .occurrence = 2, .detection = 1,
        .ap = FMEA_AP_LOW,
        .diag_func = diag_check_pressure,
        .recovery_func = NULL
    },
    [FMEA_ID_I2C_BUS] = {
        .id = FMEA_ID_I2C_BUS,
        .name = "I2C Sensor Bus",
        .severity = 6, .occurrence = 2, .detection = 1,
        .ap = FMEA_AP_LOW,
        .diag_func = diag_check_i2c,
        .recovery_func = recover_i2c_bus
    }
};

fmea_action_priority_t fmea_calculate_ap(uint8_t s, uint8_t o, uint8_t d) {
    if (s >= 9) {
        if (o >= 2) return FMEA_AP_HIGH;
        return (d >= 5) ? FMEA_AP_HIGH : FMEA_AP_MEDIUM;
    }
    if (s >= 7) {
        if (o >= 8) return FMEA_AP_HIGH;
        if (o >= 6) return (d >= 5) ? FMEA_AP_HIGH : FMEA_AP_MEDIUM;
        if (o >= 4) return (d >= 7) ? FMEA_AP_HIGH : FMEA_AP_MEDIUM;
        return (d >= 7) ? FMEA_AP_MEDIUM : FMEA_AP_LOW;
    }
    if (s >= 4) {
        if (o >= 8) return (d >= 7) ? FMEA_AP_HIGH : FMEA_AP_MEDIUM;
        if (o >= 6) return FMEA_AP_MEDIUM;
        return (d >= 7) ? FMEA_AP_MEDIUM : FMEA_AP_LOW;
    }
    return (o >= 8 && d >= 7) ? FMEA_AP_MEDIUM : FMEA_AP_LOW;
}

void fmea_init(void) {
    for (int i = 0; i < FMEA_ID_COUNT; ++i) {
        g_fmea_state[i].fail_count = 0;
        g_fmea_state[i].last_fail_timestamp_ms = 0;
        g_fmea_state[i].is_active = false;
    }
}

void fmea_run_diagnostics(uint32_t current_time_ms) {
    for (int i = 0; i < FMEA_ID_COUNT; ++i) {
        const fmea_record_t *rec = &g_fmea_registry[i];
        if (rec->diag_func == NULL) continue;

        bool is_ok = rec->diag_func();
        if (!is_ok) {
            g_fmea_state[i].fail_count++;
            g_fmea_state[i].last_fail_timestamp_ms = current_time_ms;
            g_fmea_state[i].is_active = true;

            /* Спроба локального відновлення */
            if (rec->recovery_func != NULL) {
                rec->recovery_func();
            }
        } else {
            g_fmea_state[i].is_active = false;
        }
    }
}

bool fmea_is_system_safe(void) {
    for (int i = 0; i < FMEA_ID_COUNT; ++i) {
        if (g_fmea_state[i].is_active && g_fmea_registry[i].severity >= 8) {
            return false; /* Активна критична відмова */
        }
    }
    return true;
}
