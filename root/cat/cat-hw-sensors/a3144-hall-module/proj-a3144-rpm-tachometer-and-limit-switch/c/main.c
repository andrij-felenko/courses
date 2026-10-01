#include "a3144.h"
#include <stdio.h>

/**
 * @brief Допоміжна функція симуляції зчитування стану вхідного виводу GPIO.
 */
static bool read_simulated_pin(bool magnet_present) {
    /* Давач A3144 має інверсний вихід (Active LOW):
       при наявності магніту вихід LOW (false), при відсутності HIGH (true) */
    return !magnet_present;
}

int main(void) {
    puts("=== Демонстрація C-драйвера цифрового давача Холла A3144 ===");
    puts("Режими: безконтактний кінцевий вимикач та вимірювання RPM");
    puts("------------------------------------------------------------");
    putchar(10);

    /* Конфігурація периферії давача */
    a3144_config_t config = {
        .gpio_pin = 2,                      /* Вивід GPIO2 */
        .pull_type = A3144_PULL_UP,         /* Внутрішнє підтягування до VCC */
        .exti_trigger = A3144_EXTI_TRIGGER_BOTH, /* Переривання за обома фронтами */
        .debounce_ms = 10,                  /* Програмний дебаунс 10 мс */
        .pulses_per_rev = 1,                /* 1 магніт на один оберт ротора */
        .rpm_timeout_ms = 1500              /* Скидання RPM через 1.5 с бездіяльності */
    };

    a3144_handle_t sensor;
    if (!a3144_init(&sensor, &config)) {
        puts("Помилка ініціалізації драйвера A3144!");
        return 1;
    }

    puts("Драйвер успішно ініціалізовано. Запуск суперциклу симуляції...");
    putchar(10);

    uint32_t sys_time_ms = 0;
    const uint32_t step_ms = 10;
    uint32_t last_log_time_ms = 0;

    /* Сценарій симуляції розбитий на часові інтервали */
    for (sys_time_ms = 0; sys_time_ms <= 3500; sys_time_ms += step_ms) {

        /* Тест 1: Поодиноке спрацьовування кінцевого вимикача на 200 мс */
        if (sys_time_ms == 200) {
            /* Переривання: магніт наблизився до давача (pin = LOW) */
            a3144_exti_isr_handler(&sensor, sys_time_ms, read_simulated_pin(true));
        }
        if (sys_time_ms == 450) {
            /* Переривання: магніт віддалився від давача (pin = HIGH) */
            a3144_exti_isr_handler(&sensor, sys_time_ms, read_simulated_pin(false));
        }

        /* Тест 2: Серія обертів валу з магнітом з періодом 100 мс (600 RPM) з t=800 мс до t=2000 мс */
        if (sys_time_ms >= 800 && sys_time_ms <= 2000) {
            if ((sys_time_ms % 100) == 0) {
                /* Магніт проходить повз давач */
                a3144_exti_isr_handler(&sensor, sys_time_ms, read_simulated_pin(true));
            } else if ((sys_time_ms % 100) == 30) {
                /* Магніт залишає зону виявлення */
                a3144_exti_isr_handler(&sensor, sys_time_ms, read_simulated_pin(false));
            }
        }

        /* Неблокувальна обробка станів та обчислення RPM */
        a3144_process(&sensor, sys_time_ms);

        /* Обробка асинхронних подій наближення */
        if (a3144_get_approach_event(&sensor)) {
            printf("t=%4u мс | [ПОДІЯ EXTI] Магніт НАБЛИЗИВСЯ (Вимикач ЗАМКНЕНО). Лічильник: %u",
                   sys_time_ms, (unsigned int)a3144_get_trigger_count(&sensor));
            putchar(10);
        }

        /* Обробка асинхронних подій віддалення */
        if (a3144_get_removal_event(&sensor)) {
            printf("t=%4u мс | [ПОДІЯ EXTI] Магніт ВІДДАЛИВСЯ (Вимикач РОЗІМКНЕНО)", sys_time_ms);
            putchar(10);
        }

        /* Періодичний вивід поточної швидкості та стану вимикача кожні 500 мс */
        if ((sys_time_ms - last_log_time_ms) >= 500) {
            last_log_time_ms = sys_time_ms;
            bool present = a3144_is_magnet_present(&sensor);
            float rpm = a3144_get_rpm(&sensor);
            printf("t=%4u мс | Моніторинг -> Стан: %s | Поточна швидкість: %.1f RPM",
                   sys_time_ms, present ? "ЗАМКНЕНО (Магніт)" : "РОЗІМКНЕНО (Немає)", (double)rpm);
            putchar(10);
        }
    }

    putchar(10);
    puts("=== Симуляцію успішно завершено ===");
    return 0;
}
