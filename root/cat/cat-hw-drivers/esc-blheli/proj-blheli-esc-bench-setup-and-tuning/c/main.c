#include <stdio.h>
#include <stdint.h>
#include "esc_control.h"

/**
 * @brief Допоміжна функція для симуляції значень АЦП при різному рівні напруги BEC.
 * @param target_voltage Бажана напруга BEC у вольтах.
 * @return uint16_t Сире значення 12-бітного АЦП.
 */
static uint16_t simulate_adc_reading(float target_voltage) {
    /* V_pin = V_bec / BEC_DIVIDER_RATIO */
    float v_pin = target_voltage / BEC_DIVIDER_RATIO;
    if (v_pin > BEC_VREF_VOLTS) {
        v_pin = BEC_VREF_VOLTS;
    }
    return (uint16_t)((v_pin * BEC_ADC_MAX_VALUE) / BEC_VREF_VOLTS);
}

int main(void) {
    esc_driver_t esc;

    printf("=== Ініціалізація системного регулятора ESC BLHeli 30A з BEC ===\n");
    esc_init(&esc);

    printf("Статус армування: %s\n", esc.is_armed ? "АРМОВАНО" : "НЕ АРМОВАНО");
    printf("Початковий імпульс ШІМ: %u мкс\n\n", esc.current_pulse_us);

    /* Тестові сценарії роботи з різними рівнями напруги BEC та запитами дроселя */
    struct {
        float simulated_bec_volts;
        uint16_t requested_throttle;
        const char *description;
    } test_steps[] = {
        {5.00f, 1200, "Нормальна робота (BEC 5.0В, газ 20%)"},
        {4.95f, 1500, "Нормальна робота (BEC 4.95В, газ 50%)"},
        {4.80f, 1800, "Невелике навантаження (BEC 4.80В, газ 80%)"},
        {4.65f, 1700, "Попередження про просідання (BEC 4.65В)"},
        {4.35f, 1900, "Критичне просідання BEC (4.35В) - спрацювання захисту!"},
        {5.00f, 1600, "Відновлення живлення 5.0В (але активний emergency stop)"}
    };

    size_t num_steps = sizeof(test_steps) / sizeof(test_steps[0]);

    for (size_t i = 0; i < num_steps; ++i) {
        uint16_t raw_adc = simulate_adc_reading(test_steps[i].simulated_bec_volts);

        printf("Крок %zu: %s\n", i + 1, test_steps[i].description);
        esc_process(&esc, raw_adc, test_steps[i].requested_throttle);

        const char *status_str = "OK";
        if (esc.status == BEC_STATUS_WARNING) {
            status_str = "ПОПЕРЕДЖЕННЯ";
        } else if (esc.status == BEC_STATUS_CRITICAL) {
            status_str = "КРИТИЧНО";
        }

        printf("  АЦП сире: %u -> Напруга BEC: %.2f В [Статус: %s]\n",
               raw_adc, esc.bec_voltage, status_str);
        printf("  Запитаний імпульс: %u мкс -> Фактичний ШІМ: %u мкс\n",
               test_steps[i].requested_throttle, esc.current_pulse_us);
        printf("  Аварійне блокування: %s\n\n",
               esc.emergency_stop ? "ТАК (Дросель скинуто)" : "НІ");
    }

    return 0;
}
