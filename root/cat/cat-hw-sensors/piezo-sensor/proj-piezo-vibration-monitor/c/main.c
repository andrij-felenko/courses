#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include "piezo_sensor.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/**
 * @brief Імітатор вхідного сигналу АЦП від п'єзоелектричного давача.
 *
 * Моделює спокійний стан з шумом та механічний струс із згасаючими високовольтними коливаннями.
 *
 * @param sample_index Номер поточного відліку.
 * @param baseline Базовий рівень АЦП.
 * @return Імітований відлік АЦП (0..4095).
 */
static uint16_t simulate_adc_sample(uint32_t sample_index, uint16_t baseline) {
    float signal = (float)baseline;

    /* Фоновий шум спокою (±5 LSB) */
    float noise = (float)((int)(sample_index * 7U + 3U) % 11 - 5);
    signal += noise;

    /* Перший струс: починається з відліку 100, триває близько 80 відліків */
    if (sample_index >= 100U && sample_index < 180U) {
        float t = (float)(sample_index - 100U);
        /* Згасаюче синусоїдальне коливання з початковою амплітудою 1200 LSB */
        float oscillation = 1200.0f * expf(-0.06f * t) * sinf(2.0f * (float)M_PI * 0.15f * t);
        signal += oscillation;
    }

    /* Другий слабший струс (поштовх): починається з відліку 250 */
    if (sample_index >= 250U && sample_index < 310U) {
        float t = (float)(sample_index - 250U);
        float oscillation = 500.0f * expf(-0.08f * t) * sinf(2.0f * (float)M_PI * 0.2f * t);
        signal += oscillation;
    }

    /* Обмеження діапазону 12-бітного АЦП (0..4095) */
    if (signal < 0.0f) {
        signal = 0.0f;
    }
    if (signal > 4095.0f) {
        signal = 4095.0f;
    }

    return (uint16_t)signal;
}

int main(void) {
    printf("=== Демонстрація цифрової обробки сигналу аналогового п'єзоелектричного давача ===\n\n");

    /* Конфігурація драйвера:
     * - АЦП 12 біт, базове зміщення 2048 (VCC / 2)
     * - Швидкий attack (0.7) для негайного захоплення удару
     * - Плавний decay (0.05) для утримання огинаючої
     * - Гістерезис: вмикання тривоги при огинаючій >= 500.0, вимикання при < 150.0
     */
    piezo_config_t config = {
        .baseline_adc = 2048U,
        .attack_factor = 0.70f,
        .decay_factor = 0.05f,
        .energy_alpha = 0.10f,
        .alarm_threshold_high = 500.0f,
        .alarm_threshold_low = 150.0f
    };

    piezo_sensor_t piezo;
    if (!piezo_sensor_init(&piezo, &config)) {
        printf("Помилка ініціалізації драйвера п'єзоелектричного давача!\n");
        return 1;
    }

    printf("Налаштування драйвера:\n");
    printf(" - Нульова лінія АЦП: %u LSB\n", config.baseline_adc);
    printf(" - Поріг спрацьовування тривоги (HIGH): %.1f LSB\n", config.alarm_threshold_high);
    printf(" - Поріг скидання тривоги (LOW): %.1f LSB\n", config.alarm_threshold_low);
    printf(" - Гістерезис: %.1f LSB\n\n", config.alarm_threshold_high - config.alarm_threshold_low);

    printf("Початок потокової обробки відліків АЦП (суперцикл МК)...\n\n");
    printf("  Відлік | АЦП (LSB) | Огинаюча | Енергія  | Стан тривоги\n");
    printf("---------+-----------+----------+----------+----------------------------------\n");

    bool prev_alarm = false;

    for (uint32_t i = 0U; i < 350U; i++) {
        uint16_t adc_sample = simulate_adc_sample(i, config.baseline_adc);
        piezo_sensor_process_sample(&piezo, adc_sample);

        float env = piezo_sensor_get_envelope(&piezo);
        float nrg = piezo_sensor_get_energy(&piezo);
        bool alarm = piezo_sensor_is_alarm_active(&piezo);

        /* Виводимо інформацію при зміні стану тривоги або на пікових точках */
        if (alarm != prev_alarm || (i % 25 == 0) || (i >= 100 && i <= 120 && i % 5 == 0)) {
            const char *status_str = alarm ? "!!! ТРИВОГА (ВІБРАЦІЙНА АНОМАЛІЯ) !!!" : "НОРМА";
            printf(" %7u |   %5u   | %8.1f | %8.1f | %s\n", i, adc_sample, env, nrg, status_str);
            prev_alarm = alarm;
        }
    }

    printf("---------+-----------+----------+----------+----------------------------------\n\n");
    printf("Підсумок виявлення аномалій:\n");
    printf(" - Загальна кількість підтверджених ударів: %u\n", piezo.peak_count);
    printf(" - Фінальне значення огинаючої: %.2f LSB\n", piezo_sensor_get_envelope(&piezo));
    printf(" - Фінальний стан тривоги: %s\n", piezo_sensor_is_alarm_active(&piezo) ? "АКТИВНА" : "НЕАКТИВНА");

    return 0;
}
