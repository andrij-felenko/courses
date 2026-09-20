/**
 * @file main.c
 * @brief Демонстраційний приклад роботи з драйвером пристрою дозволу.
 */

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "enabling_switch.h"

/* Симуляція імпульсного тесту короткого замикання */
static bool mock_pulse_test(uint8_t channel) {
    (void)channel;
    /* У реальній системі тут генерується тестовий 100-мкс імпульс і зчитується відповідь */
    return false; /* Помилок КЗ немає */
}

int main(void) {
    EnablingSwitch sw;
    EnablingSwitchConfig config = {
        .debounce_ms = 20,
        .discrepancy_timeout_ms = 100,
        .enable_pulse_test = true
    };

    enabling_switch_init(&sw, config);

    printf("=== Старт системи контролю трипозиційного пристрою дозволу ===\n");

    uint32_t system_time_ms = 0;
    EnablingState last_printed_state = ENABLING_STATE_FAULT;

    /* Сценарій опитування системи */
    struct {
        uint32_t time_ms;
        bool ch1;
        bool ch2;
        const char *description;
    } test_steps[] = {
        {   0, false, false, "Початковий стан: важіль відпущено" },
        { 100, true,  true,  "Натискання в Положення 2 (Робочий дозвіл)" },
        { 300, false, false, "Повернення в Положення 1 (Відпущено)" },
        { 400, true,  false, "Помилка: Канал 1 замкнено, Канал 2 відкритий (Розсинхронізація)" },
        { 600, true,  false, "Перевищення таймауту розсинхронізації (100 мс)" },
        { 700, false, false, "Скидання у вихідний стан Положення 1" },
        { 800, true,  true,  "Повторна нормальна активація після скидання" }
    };

    size_t step_count = sizeof(test_steps) / sizeof(test_steps[0]);
    size_t step_index = 0;

    while (step_index < step_count) {
        system_time_ms += 10; /* Крок системного таймера 10 мс */

        if (system_time_ms >= test_steps[step_index].time_ms) {
            printf("\n[Час: %4u мс] %s\n", system_time_ms, test_steps[step_index].description);
            step_index++;
        }

        bool ch1_input = test_steps[step_index > 0 ? step_index - 1 : 0].ch1;
        bool ch2_input = test_steps[step_index > 0 ? step_index - 1 : 0].ch2;

        EnablingState state = enabling_switch_update(&sw, ch1_input, ch2_input, system_time_ms, mock_pulse_test);

        if (state != last_printed_state) {
            printf(" -> Зміна стану FSM: %s\n", enabling_switch_state_to_str(state));
            last_printed_state = state;
        }
    }

    printf("\n=== Тестування драйвера успішно завершено ===\n");
    return 0;
}
