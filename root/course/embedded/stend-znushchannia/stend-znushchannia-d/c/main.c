#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Регістри та піни контролера стенду (апаратна абстракція) */
#define GLITCH_TIMER_PRESCALER   (84 - 1)  /* 84 МГц / 84 = 1 МГц (1 такт = 1 мкс) */

typedef enum {
    BENCH_OK = 0,
    BENCH_ERR_INVALID_PARAM = 1,
    BENCH_ERR_HARDWARE_FAULT = 2,
    BENCH_ERR_TIMEOUT = 3
} bench_status_t;

typedef struct {
    uint16_t voltage_mv;        /* Напруга живлення DUT у мілівольтах (1800..5500) */
    uint32_t dropout_us;        /* Тривалість просідання у мікросекундах (1..500000) */
    bool     spark_relay_en;    /* Увімкнення реле завад під час просідання */
    bool     active_pull_down;  /* Примусовий розряд шини живлення N-MOSFET ключем */
} bench_stress_config_t;

typedef struct {
    uint16_t measured_mv;       /* Виміряна напруга живлення */
    uint16_t current_ma;        /* Виміряний струм споживання */
    bool     dut_heartbeat_ok;  /* Наявність сигналу від DUT */
    bool     reset_triggered;   /* Чи було зафіксовано лінію RESET */
} bench_telemetry_t;

/* Прототипи апаратних функцій нижнього рівня */
void hw_dac_set_voltage_mv(uint16_t mv);
void hw_timer_configure_pulse_us(uint32_t us);
void hw_timer_start_one_pulse(void);
void hw_spark_relay_set(bool enable);
void hw_fast_pulldown_arm(bool enable);
void hw_ina226_read(uint16_t *voltage_mv, uint16_t *current_ma);
bool hw_read_dut_reset_pin(void);

/* Ініціалізація підсистем стенду */
bench_status_t bench_init(void) {
    hw_dac_set_voltage_mv(3300); /* Безпечний старт на 3.3 В */
    hw_spark_relay_set(false);
    hw_fast_pulldown_arm(false);
    return BENCH_OK;
}

/* Виконання одиничного циклу стресу за конфігурацією */
bench_status_t bench_execute_stress_cycle(const bench_stress_config_t *cfg, bench_telemetry_t *out_tel) {
    if (!cfg || !out_tel) {
        return BENCH_ERR_INVALID_PARAM;
    }
    if (cfg->voltage_mv < 1000 || cfg->voltage_mv > 5500) {
        return BENCH_ERR_INVALID_PARAM;
    }
    if (cfg->dropout_us == 0 || cfg->dropout_us > 1000000) {
        return BENCH_ERR_INVALID_PARAM;
    }

    /* 1. Встановлення фонової напруги через ЦАП */
    hw_dac_set_voltage_mv(cfg->voltage_mv);

    /* 2. Конфігурація апаратного таймера для одиночного імпульсу глітчу */
    hw_timer_configure_pulse_us(cfg->dropout_us);
    hw_fast_pulldown_arm(cfg->active_pull_down);

    /* 3. Активація реле завад, якщо потрібно */
    if (cfg->spark_relay_en) {
        hw_spark_relay_set(true);
    }

    /* 4. Запуск апаратного імпульсу розриву живлення */
    hw_timer_start_one_pulse();

    /* 5. Вимкнення реле після завершення імпульсу */
    if (cfg->spark_relay_en) {
        hw_spark_relay_set(false);
    }

    /* 6. Збір телеметрії після повернення живлення */
    hw_ina226_read(&out_tel->measured_mv, &out_tel->current_ma);
    out_tel->reset_triggered = hw_read_dut_reset_pin();
    out_tel->dut_heartbeat_ok = (out_tel->current_ma > 5) && !out_tel->reset_triggered;

    return BENCH_OK;
}
