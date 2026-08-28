#include <stdint.h>
#include <stdbool.h>

/* Прототипи апаратних функцій плати */
void hw_power_switch_set(bool enable);
void hw_gpio_set_mode_analog(void);
void hw_gpio_restore_uart_and_ctrl(void);
void hw_pwrkey_pulse(uint32_t duration_ms);
bool hw_get_status_pin(void);
void delay_ms(uint32_t ms);

/* Повна послідовність апаратного знеструмлення та безпечного перезапуску */
bool smart_module_hard_power_cycle(void) {
    /* Крок 1: Ізоляція ліній. Переводимо ВСІ підключені піни МК в стан High-Z (Analog Input) */
    hw_gpio_set_mode_analog();

    /* Крок 2: Знеструмлюємо модуль через розмикання High-Side P-MOSFET ключа */
    hw_power_switch_set(false);

    /* Крок 3: Витримуємо паузу для повного розряду блокувальних конденсаторів */
    delay_ms(1000);

    /* Крок 4: Подаємо напругу VBAT назад на модуль */
    hw_power_switch_set(true);

    /* Крок 5: Очікуємо стабілізації перехідних процесів живлення (t_ramp) */
    delay_ms(200);

    /* Крок 6: Відновлюємо конфігурацію GPIO (UART TX/RX, DTR, PWRKEY) */
    hw_gpio_restore_uart_and_ctrl();

    /* Крок 7: Генеруємо імпульс увімкнення на PWRKEY (наприклад, 1000 мс) */
    hw_pwrkey_pulse(1000);

    /* Крок 8: Очікуємо підйому лінії STATUS (до 5 секунд) */
    bool ready = false;
    for (uint32_t i = 0; i < 50; ++i) {
        delay_ms(100);
        if (hw_get_status_pin()) {
            ready = true;
            break;
        }
    }

    return ready;
}
