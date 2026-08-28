#include <stdint.h>
#include <stdbool.h>

/* Коди причин апаратного перезапуску системи */
typedef enum {
    RESET_CAUSE_UNKNOWN      = 0x00,
    RESET_CAUSE_POWER_ON     = 0x01,
    RESET_CAUSE_BROWNOUT     = 0x02, /* Просадка живлення через перехідний процес */
    RESET_CAUSE_WATCHDOG     = 0x03, /* Зависання через перешкоду або втрату тактування */
    RESET_CAUSE_THERMAL_LOCK = 0x04  /* Захисне вимкнення через перегрів */
} reset_cause_t;

/* Структура стану фізичного середовища */
typedef struct {
    float    temperature_c;
    float    supply_voltage_v;
    uint32_t brownout_count;
    bool     throttling_active;
    bool     heater_active;
} system_telemetry_t;

/* Емуляція апаратних регістрів мікроконтролера */
extern uint32_t MCU_RESET_FLAGS_REG;
extern void mcu_set_cpu_frequency_mhz(uint32_t freq);
extern void mcu_disable_high_power_peripherals(void);
extern void mcu_enable_high_power_peripherals(void);
extern void nonvolatile_log_write(reset_cause_t cause);

/* Зчитування та фіксація причини останнього перезапуску */
reset_cause_t system_diagnose_boot_cause(void) {
    reset_cause_t cause = RESET_CAUSE_UNKNOWN;
    uint32_t flags = MCU_RESET_FLAGS_REG;

    if (flags & (1 << 3)) {
        cause = RESET_CAUSE_BROWNOUT;
    } else if (flags & (1 << 2)) {
        cause = RESET_CAUSE_WATCHDOG;
    } else if (flags & (1 << 0)) {
        cause = RESET_CAUSE_POWER_ON;
    }

    /* Очищення регістру прапорів після зчитування */
    MCU_RESET_FLAGS_REG = 0;
    nonvolatile_log_write(cause);
    return cause;
}

/* Обробка стрес-факторів середовища в головному циклі керування */
void system_environmental_guard(system_telemetry_t *telemetry) {
    /* 1. Захист від перегріву: динамічне зниження частоти */
    if (telemetry->temperature_c >= 80.0f) {
        if (!telemetry->throttling_active) {
            mcu_set_cpu_frequency_mhz(24); /* Скидаємо тактову частоту з 160 МГц */
            mcu_disable_high_power_peripherals();
            telemetry->throttling_active = true;
        }
    } else if (telemetry->temperature_c <= 65.0f && telemetry->throttling_active) {
        mcu_set_cpu_frequency_mhz(160); /* Повертаємо номінальну швидкість */
        mcu_enable_high_power_peripherals();
        telemetry->throttling_active = false;
    }

    /* 2. Захист від замерзання електролітів та конденсату: увімкнення підігріву */
    if (telemetry->temperature_c < -10.0f) {
        telemetry->heater_active = true;
    } else if (telemetry->temperature_c > 0.0f) {
        telemetry->heater_active = false;
    }

    /* 3. Контроль просадки напруги живлення під навантаженням */
    if (telemetry->supply_voltage_v < 3.10f) {
        /* Напруга наближається до порогу UVLO (2.9 В) — аварійне вимкнення передавача */
        mcu_disable_high_power_peripherals();
    }
}
