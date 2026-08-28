/* cold_boot_manager.c - Реалізація менеджера холодного пуску на мові C */
#include <stdint.h>
#include <stdbool.h>

#define TEMP_FREEZING_LIMIT_C   0     /* Границя блокування заряду: 0 °C */
#define TEMP_DEEP_COLD_LIMIT_C -10    /* Границя глибокого холоду: -10 °C */
#define HSE_STARTUP_TIMEOUT_CYCLES 500000

typedef enum {
    SYSTEM_CLK_HSI = 0,
    SYSTEM_CLK_HSE_PLL = 1
} ClockSource_t;

typedef enum {
    PWR_PROFILE_SAFE_COLD = 0,
    PWR_PROFILE_WARMING_UP = 1,
    PWR_PROFILE_FULL_POWER = 2
} PowerProfile_t;

typedef struct {
    int16_t temperature_c;
    uint16_t vbat_mv;
    uint16_t estimated_esr_mohm;
    ClockSource_t active_clock;
    PowerProfile_t pwr_profile;
    bool charge_allowed;
} ColdSystemStatus_t;

/* Симуляція регістрів апаратного рівня */
static volatile uint32_t MOCK_RCC_CR = 0x00000001; /* HSI ON */
#define RCC_CR_HSIRDY (1 << 1)
#define RCC_CR_HSEON  (1 << 16)
#define RCC_CR_HSERDY (1 << 17)

/* Запуск нагрівача плати (PCB Trace Heater) через ШІМ */
void hw_set_board_heater_pwm(uint8_t duty_percent) {
    /* Налаштування апаратного таймера ШІМ для нагрівального польового ключа */
    (void)duty_percent;
}

/* Блокування/дозвіл апаратного ключа заряджання в мікросхемі Charger IC */
void hw_set_charge_enable(bool enable) {
    /* Керування піном CHG_EN або регістром I2C зарядного пристрою */
    (void)enable;
}

/* Виконання блоку dummy-обчислень для саморозігріву кристала MCU */
void mcu_execute_dummy_burn_cycle(uint32_t iterations) {
    volatile float acc = 1.0001f;
    for (uint32_t i = 0; i < iterations; ++i) {
        acc = (acc * 1.00003f) + 0.00007f;
    }
    (void)acc;
}

/* Спроба безпечного запуску зовнішнього кварцу HSE з таймаутом */
bool clock_try_enable_hse_with_timeout(void) {
    MOCK_RCC_CR |= RCC_CR_HSEON; /* Вмикаємо осцилятор HSE */
    
    uint32_t timeout = HSE_STARTUP_TIMEOUT_CYCLES;
    while (!(MOCK_RCC_CR & RCC_CR_HSERDY)) {
        if (--timeout == 0) {
            /* Кварц не запустився через мороз або конденсат - вимикаємо для економії */
            MOCK_RCC_CR &= ~RCC_CR_HSEON;
            return false;
        }
    }
    return true;
}

/* Оцінка внутрішнього опору акумулятора за стрибком напруги */
uint16_t battery_estimate_esr(uint16_t v_ocv_mv, uint16_t v_load_mv, uint16_t i_pulse_ma) {
    if (v_ocv_mv <= v_load_mv || i_pulse_ma == 0) {
        return 50; /* Номінальний опір за замовчуванням */
    }
    uint32_t delta_v = (uint32_t)(v_ocv_mv - v_load_mv);
    /* ESR (мОм) = (ΔV (мВ) * 1000) / I (мА) */
    return (uint16_t)((delta_v * 1000U) / i_pulse_ma);
}

/* Головний автомат адаптивного холодного старту */
void cold_boot_orchestrator(int16_t current_temp_c, uint16_t v_unloaded_mv, uint16_t v_loaded_mv) {
    ColdSystemStatus_t status;
    status.temperature_c = current_temp_c;
    status.vbat_mv = v_loaded_mv;
    status.active_clock = SYSTEM_CLK_HSI;
    status.estimated_esr_mohm = battery_estimate_esr(v_unloaded_mv, v_loaded_mv, 200);

    /* 1. Захист акумулятора: повна заборона заряду нижче 0 °C */
    if (status.temperature_c <= TEMP_FREEZING_LIMIT_C) {
        status.charge_allowed = false;
        hw_set_charge_enable(false);
    } else {
        status.charge_allowed = true;
        hw_set_charge_enable(true);
    }

    /* 2. Обробка глибокого морозу */
    if (status.temperature_c <= TEMP_DEEP_COLD_LIMIT_C || status.estimated_esr_mohm > 500) {
        status.pwr_profile = PWR_PROFILE_SAFE_COLD;
        
        /* Вмикаємо активний нагрів плати */
        hw_set_board_heater_pwm(80);
        
        /* Запускаємо саморозігрів ядра CPU dummy-обчисленнями */
        mcu_execute_dummy_burn_cycle(2000000);
        
        /* Залишаємось на безпечному внутрішньому HSI-генераторі */
        status.active_clock = SYSTEM_CLK_HSI;
    } else {
        /* Температура в нормі або прогрів завершено - запускаємо зовнішній кварц */
        hw_set_board_heater_pwm(0);
        
        if (clock_try_enable_hse_with_timeout()) {
            status.active_clock = SYSTEM_CLK_HSE_PLL;
            status.pwr_profile = PWR_PROFILE_FULL_POWER;
        } else {
            /* Кварц зірвано: залишаємось на HSI та знижуємо навантаження */
            status.active_clock = SYSTEM_CLK_HSI;
            status.pwr_profile = PWR_PROFILE_WARMING_UP;
        }
    }
}
