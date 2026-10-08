#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "adc.h"
#include "servo.h"

/**
 * @file main.c
 * @brief Головна програма керування RC-сервоприводом від потенціометра.
 *
 * Демонструє неблокуюче зчитування аналогового сигналу потенціометра,
 * лінійне мапування відліків АЦП у тривалість позитивного ШІМ-імпульсу (0.5 мс .. 2.5 мс)
 * з періодом кадру 20 мс та оновлення регістрів порівняння таймера мікроконтролера.
 */

int main(void)
{
    printf("===============================================================\n");
    printf("  Керування RC-сервоприводом через ШІМ та АЦП потенціометра    \n");
    printf("===============================================================\n\n");

    /* 1. Конфігурація та ініціалізація модуля АЦП */
    adc_config_t adc_cfg = {
        .channel = 0,
        .prescaler = 128,
        .use_internal_vref = true
    };
    adc_init(&adc_cfg);
    printf("[АЦП] Ініціалізовано: Розрядність = %d біт (0..%d), VREF = %d мВ\n",
           ADC_RESOLUTION_BITS, ADC_MAX_VALUE, ADC_VREF_MV);

    /* 2. Конфігурація та ініціалізація драйвера сервоприводу */
    servo_t servo;
    bool init_ok = servo_init(&servo, 1, SERVO_MIN_PULSE_US, SERVO_MAX_PULSE_US);
    if (!init_ok) {
        printf("[ПОМИЛКА] Не вдалося ініціалізувати драйвер сервоприводу!\n");
        return 1;
    }

    /* Активація генерації ШІМ-сигналу */
    servo_enable(&servo, true);

    printf("[ШІМ] Період кадру: %d мс (%d мкс, 50 Гц)\n", SERVO_FRAME_PERIOD_MS, SERVO_FRAME_PERIOD_US);
    printf("[ШІМ] Діапазон імпульсу: %d мкс (0.5 мс -> 0 deg) .. %d мкс (2.5 мс -> 180 deg)\n",
           SERVO_MIN_PULSE_US, SERVO_MAX_PULSE_US);
    printf("[ТАЙМЕР] Частота: %lu Гц, Преддільник: %d, Такти периоду ICR: %lu\n\n",
           SERVO_CPU_FREQ_HZ / SERVO_TIMER_PRESCALER, SERVO_TIMER_PRESCALER,
           servo_pulse_us_to_timer_ticks(SERVO_FRAME_PERIOD_US));

    /* 3. Демонстраційна серія неблокуючого мапування різних положень потенціометра */
    uint16_t test_adc_inputs[] = {0, 256, 512, 768, 1023};
    size_t num_tests = sizeof(test_adc_inputs) / sizeof(test_adc_inputs[0]);

    printf("--- Перебіг неблокуючого циклу мапування у реальному часі ---\n");
    for (size_t i = 0; i < num_tests; i++) {
        uint16_t adc_raw = test_adc_inputs[i];

        /* Оновлення стану сервоприводу відповідно до оцифрованого аналогового відліку */
        servo_update_from_adc(&servo, adc_raw, ADC_MAX_VALUE);

        float voltage_mv = adc_to_millivolts(adc_raw);

        printf("Крок %zu:\n", i + 1);
        printf("  Відлік АЦП:          %4d / %d (Напруга: %.1f мВ)\n", adc_raw, ADC_MAX_VALUE, voltage_mv);
        printf("  Тривалість імпульсу: %4d мкс (%.2f мс)\n", servo.current_pulse_us, (float)servo.current_pulse_us / 1000.0f);
        printf("  Розрахований кут:    %5.1f град\n", servo.current_angle_deg);
        printf("  Регістр порівняння:  %5lu тактів таймера\n\n", servo.timer_ticks);
    }

    printf("===============================================================\n");
    printf("  Програму успішно виконано. ШІМ працює без блокування циклу.  \n");
    printf("===============================================================\n");

    return 0;
}
