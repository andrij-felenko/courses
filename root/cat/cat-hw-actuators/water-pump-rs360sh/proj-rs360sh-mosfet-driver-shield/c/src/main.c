#include <stdio.h>
#include <stdlib.h>
#include "pump_pwm.h"

/**
 * @file main.c
 * @brief Точка входу демонстраційної програми плавної регуляції помпи RS-360SH.
 */

/* Допоміжна функція перетворення стану в український рядок для моніторингу */
static const char* state_to_string(pump_state_t state) {
    switch (state) {
        case PUMP_STATE_STOPPED:        return "ЗУПИНЕНО";
        case PUMP_STATE_RAMPING:        return "РАМПА (ЗМІНА)";
        case PUMP_STATE_RUNNING:        return "СТАБІЛЬНО";
        case PUMP_STATE_EMERGENCY_STOP: return "АВАРІЙНИЙ ЗУПИН";
        case PUMP_STATE_FAULT:          return "ПОМИЛКА";
        default:                        return "НЕВІДОМО";
    }
}

int main(void) {
    printf("========================================================================\n");
    printf("  ДЕМОНСТРАЦІЯ НИЗЬКОРІВНЕВОГО C-ДРАЙВЕРА ВОДЯНОЇ ПОМПИ RS-360SH\n");
    printf("========================================================================\n\n");

    /* Симуляція периферичного апаратного таймера МК */
    timer_reg_t mcu_timer_hw = {0};

    /* Налаштування параметрів конфігурації помпи RS-360SH */
    pump_config_t config = {
        .timer_hw = &mcu_timer_hw,
        .sys_clock_hz = 72000000U,            /* 72 МГц системна частота тактування MCU */
        .pwm_freq_hz = RS360SH_DEFAULT_PWM_FREQ_HZ, /* 10 кГц частота ШІМ */
        .min_operational_duty = RS360SH_MIN_OPERATIONAL_DUTY_PCT, /* 20% поріг трогання */
        .max_operational_duty = RS360SH_MAX_OPERATIONAL_DUTY_PCT, /* 100% max */
        .ramp_rate_pct_per_sec = 40.0f,       /* 40% за секунду (розгін 0->100% за 2.5 с) */
        .max_flow_ml_min = RS360SH_MAX_FLOW_RATE_ML_MIN /* 1800 мл/хв */
    };

    pump_t pump;

    /* КРОК 1: ІНІЦІАЛІЗАЦІЯ ДРАЙВЕРА ТА НАЛАШТУВАННЯ РЕГІСТРІВ */
    printf("[1] Ініціалізація периферійного таймера та драйвера помпи...\n");
    pump_err_t err = pump_init(&pump, &config);
    if (err != PUMP_OK) {
        printf("Критична помилка ініціалізації: %s\n", pump_err_to_str(err));
        return EXIT_FAILURE;
    }

    printf("    Апаратні регістри таймера успішно заінстальовані:\n");
    printf("    - PSC (Prescaler):    %u\n", mcu_timer_hw.PSC);
    printf("    - ARR (Auto-reload):  %u (Період ШІМ)\n", mcu_timer_hw.ARR);
    printf("    - CR1:                0x%08X (CEN=%u, ARPE=%u)\n", 
           mcu_timer_hw.CR1, (mcu_timer_hw.CR1 & TIMER_CR1_CEN) != 0, (mcu_timer_hw.CR1 & TIMER_CR1_ARPE) != 0);
    printf("    - CCMR1:              0x%08X (PWM Mode 1)\n", mcu_timer_hw.CCMR1);
    printf("    - CCER:               0x%08X (CH1 Output Enable)\n", mcu_timer_hw.CCER);
    printf("    - BDTR:               0x%08X (Main Output Enable MOE)\n\n", mcu_timer_hw.BDTR);

    uint32_t current_time_ms = 0U;

    /* КРОК 2: ПЛАВНИЙ РОЗГІН ДО 75% ОБЕРТІВ (SOFT START) */
    printf("[2] Запит плавної зміни обертів (Soft Start) до 75.0%% ШІМ...\n");
    pump_set_speed(&pump, 75.0f);

    printf("  -----------------------------------------------------------------------------------------\n");
    printf("  | Час (мс) | Стан         | ШІМ (%%) | CCR1 / ARR  | Напруга (В) | Подача (мл/хв) | Об'єм (мл) |\n");
    printf("  -----------------------------------------------------------------------------------------\n");

    /* Цикл симуляції часу з кроком 100 мс */
    for (int i = 0; i < 25; ++i) {
        pump_update(&pump, current_time_ms);

        float cur_speed = pump_get_current_speed(&pump);
        float effective_voltage = (cur_speed / 100.0f) * RS360SH_NOMINAL_VOLTAGE_V;
        float flow_rate = pump_get_estimated_flow_ml_min(&pump);
        double total_vol = pump_get_total_volume_ml(&pump);

        printf("  | %8u | %-12s | %7.1f | %4u / %4u | %11.2f | %14.1f | %10.2f |\n",
               current_time_ms,
               state_to_string(pump_get_state(&pump)),
               cur_speed,
               mcu_timer_hw.CCR1,
               mcu_timer_hw.ARR,
               effective_voltage,
               flow_rate,
               total_vol);

        current_time_ms += 100U;
    }
    printf("  -----------------------------------------------------------------------------------------\n\n");

    /* КРОК 3: ЗБІЛЬШЕННЯ ШВИДКОСТІ ДО МАКСИМУМУ (100%) */
    printf("[3] Форсування обертів помпи до 100.0%% (Максимальна подача рідини)...\n");
    pump_set_speed(&pump, 100.0f);

    for (int i = 0; i < 10; ++i) {
        pump_update(&pump, current_time_ms);
        current_time_ms += 100U;
    }
    printf("    Поточний стан: %s | ШІМ: %.1f%% | Подача: %.1f мл/хв | Всього: %.2f мл\n\n",
           state_to_string(pump_get_state(&pump)),
           pump_get_current_speed(&pump),
           pump_get_estimated_flow_ml_min(&pump),
           pump_get_total_volume_ml(&pump));

    /* КРОК 4: СПРОБА ВСТАНОВЛЕННЯ НЕБЕЗПЕЧНОГО НИЗЬКОГО ШІМ (10%) */
    printf("[4] Перевірка захисту від заклинювання: Запит 10.0%% ШІМ (менше порогу 20.0%%)...\n");
    pump_set_speed(&pump, 10.0f);
    printf("    Запитано 10.0%% -> Драйвер автоматично скоригував ціль до безпечного порогу: %.1f%%\n", 
           pump.target_duty_pct);

    for (int i = 0; i < 15; ++i) {
        pump_update(&pump, current_time_ms);
        current_time_ms += 100U;
    }
    printf("    Поточний стан: %s | ШІМ: %.1f%% | Подача: %.1f мл/хв\n\n",
           state_to_string(pump_get_state(&pump)),
           pump_get_current_speed(&pump),
           pump_get_estimated_flow_ml_min(&pump));

    /* КРОК 5: ПЛАВНЕ ГАЛЬМУВАННЯ ДО 0% (SOFT STOP) */
    printf("[5] Виконання плавної зупинки помпи (Soft Stop до 0.0%%)...\n");
    pump_stop(&pump);

    for (int i = 0; i < 10; ++i) {
        pump_update(&pump, current_time_ms);
        current_time_ms += 100U;
    }
    printf("    Поточний стан: %s | ШІМ: %.1f%% | CCR1: %u\n\n",
           state_to_string(pump_get_state(&pump)),
           pump_get_current_speed(&pump),
           mcu_timer_hw.CCR1);

    /* КРОК 6: АВАРІЙНИЙ ЗУПИН (EMERGENCY SHUTDOWN) */
    printf("[6] Симуляція аварійної зупинки emergency_stop() під час розгону...\n");
    pump_set_speed(&pump, 90.0f);
    pump_update(&pump, current_time_ms);
    current_time_ms += 50U;
    pump_update(&pump, current_time_ms);

    printf("    Стан під час розгону: ШІМ = %.1f%%, CCR1 = %u\n", 
           pump_get_current_speed(&pump), mcu_timer_hw.CCR1);

    printf("    --> СПРАЦЬОВУВАННЯ АВАРІЙНОГО СИГНАЛУ!\n");
    pump_emergency_stop(&pump);

    printf("    Стан після emergency_stop(): %s | ШІМ = %.1f%% | CCR1 = %u\n\n",
           state_to_string(pump_get_state(&pump)),
           pump_get_current_speed(&pump),
           mcu_timer_hw.CCR1);

    /* ЗВІТ */
    printf("========================================================================\n");
    printf("  ПІДСУМКОВА ТЕЛЕМЕТРІЯ ТЕСТОВОГО ПРОГОНУ ВОДЯНОЇ ПОМПИ:\n");
    printf("  - Загальний прокачаний об'єм рідини: %.2f мл (%.3f літрів)\n", 
           pump_get_total_volume_ml(&pump), pump_get_total_volume_ml(&pump) / 1000.0);
    printf("  - Підсумковий стан драйвера:          %s\n", state_to_string(pump_get_state(&pump)));
    printf("========================================================================\n");

    return EXIT_SUCCESS;
}
