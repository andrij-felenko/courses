/**
 * @file main.c
 * @brief Демонстраційний додаток для тестування низькорівневого C-драйвера лазерного модуля.
 *
 * Демонструє роботу з апаратною абстракцією таймера в режимі One-Pulse,
 * зовнішнє переривання EXTI від камери машинного зору, роботу цифрового
 * медіанного фільтра АЦП та реакцію кінцевого автомата на аварійні ситуації.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "laser_driver.h"

/* Екземпляр апаратних регістрів таймера для емуляції/роботи на системі */
static laser_hw_timer_t g_mock_tim1;

/* Екземпляр дескриптора лазерного модуля */
static laser_device_t g_laser_dev;

/**
 * @brief Допоміжна функція виводу назви стану FSM українською мовою.
 */
static const char *get_state_name(laser_state_t state) {
    switch (state) {
        case LASER_STATE_DISABLED:   return "DISABLED (Вимкнено)";
        case LASER_STATE_READY:      return "READY (Готовий до стробу)";
        case LASER_STATE_STROBING:   return "STROBING (Генерація спалаху)";
        case LASER_STATE_CONTINUOUS: return "CONTINUOUS (Неперервний ШІМ)";
        case LASER_STATE_FAULT:      return "FAULT (Аварійне блокування)";
        default:                     return "UNKNOWN";
    }
}

/**
 * @brief Допоміжна функція виводу коду помилки.
 */
static const char *get_fault_name(laser_fault_t fault) {
    switch (fault) {
        case LASER_FAULT_NONE:             return "NONE (Помилок немає)";
        case LASER_FAULT_OVERTEMP:         return "OVERTEMP (Перегрів кристала)";
        case LASER_FAULT_OVERPOWER_COD:    return "OVERPOWER_COD (Загроза COD деградації)";
        case LASER_FAULT_INTERLOCK_OPEN:   return "INTERLOCK_OPEN (Розімкнено контур безпеки)";
        case LASER_FAULT_WATCHDOG_TIMEOUT: return "WATCHDOG_TIMEOUT (Таймаут випромінювання)";
        case LASER_FAULT_ADC_UNSTABLE:     return "ADC_UNSTABLE (Недостовірний АЦП)";
        default:                           return "UNKNOWN_FAULT";
    }
}

int main(void) {
    printf("=== Драйвер лазерного модуля лінійного профілю (C99 / STM32) ===\n\n");

    /* 1. Конфігурація робочих параметрів драйвера */
    laser_config_t config = {
        .timer_clock_hz = 84000000U,     /* Тактова частота шини APB2 таймера TIM1 (84 МГц) */
        .default_strobe_us = 1200U,      /* Тривалість стробу під експозицію камери (1.2 мс) */
        .pwm_frequency_hz = 25000U,      /* 25 кГц (поза межами чутності людського вуха) */
        .pwm_duty_permille = 500U,       /* 50% середньої оптичної потужності */
        .max_temp_celsius = 48.0f,       /* Критична температура діода (+48 C) */
        .max_photodiode_raw = 3200U,     /* Поріг фотодетектора: запобігання COD (0..4095) */
        .min_photodiode_raw = 50U,       /* Контроль наявності зворотного струму */
        .watchdog_timeout_ms = 25U       /* Апаратний таймаут захисту від залипання (25 мс) */
    };

    /* Ініціалізація драйвера */
    if (!laser_driver_init(&g_laser_dev, &g_mock_tim1, &config)) {
        printf("Помилка: не вдалося ініціалізувати драйвер лазера!\n");
        return 1;
    }
    printf("[1] Драйвер успішно ініціалізовано. Початковий стан: %s\n",
           get_state_name(laser_driver_get_state(&g_laser_dev)));

    /* 2. Замикання зовнішнього контуру безпеки (інтерлоку захисного кожуха) */
    laser_driver_set_interlock(&g_laser_dev, true);
    laser_driver_process_fsm(&g_laser_dev, 10);
    printf("[2] Інтерлок замкнено. Стан після FSM: %s\n\n",
           get_state_name(laser_driver_get_state(&g_laser_dev)));

    /* 3. Симуляція роботи зі строб-імпульсами камери машинного зору (3 кадри при 30 FPS) */
    printf("--- Етап 1: Синхронізація з кадровим стробом камери (EXTI -> One-Pulse) ---\n");
    uint32_t current_time_ms = 100;

    for (int frame = 1; frame <= 3; ++frame) {
        current_time_ms += 33; /* ~30 кадрів/с */

        /* Імітуємо надходження імпульсу камери на лінію EXTI */
        laser_driver_on_exti_trigger_isr(&g_laser_dev);

        /* Опитування АЦП фотодіода та термістора з випадковими шумами */
        uint16_t simulated_pd = 1850U + (uint16_t)(frame * 20);
        uint16_t simulated_temp_mv = 1050U; /* ~30 C */

        /* Вносимо поодинокий імпульсний сплеск шуму напруги для перевірки медіанного фільтра */
        if (frame == 2) {
            laser_driver_update_adc_samples(&g_laser_dev, 4000U, simulated_temp_mv); /* Одиночна завада */
        }
        laser_driver_update_adc_samples(&g_laser_dev, simulated_pd, simulated_temp_mv);

        /* Крок кінцевого автомата під час спалаху */
        laser_driver_process_fsm(&g_laser_dev, current_time_ms);

        /* Емуляція завершення імпульсу One-Pulse таймером апаратно (скидання біта CEN) */
        g_mock_tim1.CR1 &= ~(1U << 0);
        laser_driver_process_fsm(&g_laser_dev, current_time_ms + 2);

        laser_telemetry_t tel;
        laser_driver_get_telemetry(&g_laser_dev, &tel);

        printf("  Кадр %d: стан = %s | Спалахів = %u | PD = %u відл. | T = %.1f C\n",
               frame,
               get_state_name(laser_driver_get_state(&g_laser_dev)),
               tel.pulse_count,
               tel.filtered_photodiode_raw,
               tel.filtered_temperature_c);
    }

    /* 4. Тестування неперервного режиму ШІМ для регулювання потужності */
    printf("\n--- Етап 2: Перехід у неперервний режим ШІМ (CW Mode 25 кГц, 50%%) ---\n");
    laser_driver_configure_pwm(&g_laser_dev, 25000U, 500U);
    g_laser_dev.state = LASER_STATE_CONTINUOUS;
    printf("  Стан таймера: ARR = %u | CCR1 = %u | PSC = %u | CEN = %u\n",
           g_mock_tim1.ARR, g_mock_tim1.CCR1, g_mock_tim1.PSC, (g_mock_tim1.CR1 & 1U));
    printf("  Стан FSM: %s\n", get_state_name(laser_driver_get_state(&g_laser_dev)));

    /* 5. Симуляція аварійної ситуації: загроза COD (перевищення оптичної потужності) */
    printf("\n--- Етап 3: Спрацювання апаратного захисту від COD (перевищення порогу PD) ---\n");
    current_time_ms += 10;
    /* Записуємо серію надвисоких значень фотодіода (аварійний стрибок потужності струму накачки) */
    for (int k = 0; k < 4; ++k) {
        laser_driver_update_adc_samples(&g_laser_dev, 3600U, 1100U);
    }
    laser_driver_process_fsm(&g_laser_dev, current_time_ms);

    printf("  Стан після аварійного сплеску: %s\n",
           get_state_name(laser_driver_get_state(&g_laser_dev)));
    printf("  Код помилки: %s\n",
           get_fault_name(g_laser_dev.fault_code));
    printf("  Апаратний стан виходу таймера (CC1E): %u (0 = вимкнено/безпечно)\n",
           (g_mock_tim1.CCER & 1U));

    /* 6. Відновлення після усунення аварії */
    printf("\n--- Етап 4: Усунення аварійних умов та відновлення роботи ---\n");
    /* Нормалізуємо показники фотодіода */
    for (int k = 0; k < LASER_MEDIAN_WINDOW_SIZE; ++k) {
        laser_driver_update_adc_samples(&g_laser_dev, 1500U, 1020U);
    }
    bool reset_ok = laser_driver_reset_fault(&g_laser_dev);
    printf("  Спроба скидання аварії: %s\n", reset_ok ? "УСПІШНО" : "ВІДХИЛЕНО");
    printf("  Поточний стан FSM: %s\n",
           get_state_name(laser_driver_get_state(&g_laser_dev)));

    printf("\n=== Тестування C-драйвера успішно завершено ===\n");
    return 0;
}
