#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "mosfet_driver.h"

/**
 * @file main.c
 * @brief Демонстраційний приклад прямого керування силовим MOSFET логічного рівня.
 */

/* Імітація апаратних ресурсів мікроконтролера */

static void mcu_gpio_write_pin(uint8_t pin_id, bool state)
{
    printf("  [HAL GPIO] Пін %u -> %s (%s)\n",
           pin_id,
           state ? "HIGH (1)" : "LOW (0)",
           state ? "Затвор на VCC: Насичення (Ключ ВІДКРИТО)" : "Затвор на GND: Відсічка (Ключ ЗАКРИТО)");
}

static void mcu_pwm_set_duty_cycle(uint8_t pwm_channel, uint8_t duty_percent)
{
    printf("  [HAL PWM]  Канал ШІМ %u -> Заповнення: %u%%\n", pwm_channel, duty_percent);
}

static void mcu_peripherals_init(void)
{
    printf("--- Налаштування апаратної периферії МК ---\n");
    printf(" 1. GPIO Pin 12: налаштовано як Push-Pull вихід із подтяжкою Pull-Down (10 кОм на платі).\n");
    printf(" 2. Таймер PWM: налаштовано частоту ШІМ 10 кГц для швидкого перемикання ключа.\n\n");
}

static void print_mosfet_status(const mosfet_driver_t *driver, const char *step_name)
{
    mosfet_mode_t mode;
    uint8_t duty;
    if (mosfet_get_status(driver, &mode, &duty) == MOSFET_OK) {
        const char *mode_str = "НЕВІДОМО";
        switch (mode) {
        case MOSFET_MODE_OFF: mode_str = "ВИМКНЕНО (Відсічка / Pull-Down)"; break;
        case MOSFET_MODE_ON:  mode_str = "УВІМКНЕНО (Повне насичення / Min R_DS(on))"; break;
        case MOSFET_MODE_PWM: mode_str = "ШІМ-РЕГУЛЮВАННЯ (Динамічна комутація)"; break;
        }
        printf(" -> Status [%s]: Режим = %s, Скважність = %u%%\n", step_name, mode_str, duty);
    }
}

int main(void)
{
    printf("=== Демонстратор прямого керування силовим MOSFET логічного рівня ===\n\n");

    /* 0. Аналіз сумісності популярних ключових MOSFET за V_GS(th) */
    printf("--- Оцінка сумісності транзисторів із логічним керуванням (3.3В / 5В) ---\n");

    struct {
        const char *model;
        uint16_t vgs_th_max_mv;
        const char *type;
    } transistors[] = {
        {"IRLZ44N",  2000, "Logic-Level N-Ch (3.3V/5V compatible)"},
        {"IRL540N",  2000, "Logic-Level N-Ch (3.3V/5V compatible)"},
        {"IRL2203N", 1000, "Ultra-Low Logic-Level N-Ch (3.3V compatible)"},
        {"FDD8447L", 1500, "PowerTrench Logic-Level N-Ch (3.3V compatible)"},
        {"IRF540N",  4000, "Standard MOSFET (requires 10V gate drive!)"}
    };

    for (size_t i = 0; i < sizeof(transistors)/sizeof(transistors[0]); i++) {
        bool comp_3v3 = mosfet_is_logic_level_compatible(MOSFET_DRIVE_3V3, transistors[i].vgs_th_max_mv);
        bool comp_5v0 = mosfet_is_logic_level_compatible(MOSFET_DRIVE_5V0, transistors[i].vgs_th_max_mv);

        printf(" * %-9s (V_GS(th) max = %4u мВ | %s):\n",
               transistors[i].model, transistors[i].vgs_th_max_mv, transistors[i].type);
        printf("    - Керування 3.3В: %s\n", comp_3v3 ? "СУМІСНИЙ (Повне відкриття)" : "НЕ РЕКОМЕНДОВАНО (Загроза лінійного режиму та перегріву)");
        printf("    - Керування 5.0В: %s\n", comp_5v0 ? "СУМІСНИЙ (Повне відкриття)" : "НЕ РЕКОМЕНДОВАНО (Потрібен драйвер затвора 10В)");
    }
    printf("\n");

    /* 1. Ініціалізація апаратної периферії МК */
    mcu_peripherals_init();

    /* 2. Конфігурація драйвера для силового ключа IRLZ44N (3.3 В керування з ШІМ) */
    mosfet_config_t config = {
        .gpio_pin = 12,
        .pwm_channel = 1,
        .use_pwm = true,
        .drive_voltage = MOSFET_DRIVE_3V3,
        .gpio_write = mcu_gpio_write_pin,
        .pwm_set_duty = mcu_pwm_set_duty_cycle
    };

    mosfet_driver_t mosfet;

    printf("--- Ініціалізація драйвера силового ключа (з гарантованим Pull-Down) ---\n");
    mosfet_status_t status = mosfet_init(&mosfet, &config);
    if (status != MOSFET_OK) {
        printf("Помилка ініціалізації драйвера MOSFET: %d\n", status);
        return 1;
    }
    print_mosfet_status(&mosfet, "Safe Boot");
    printf(" [ОК] Затвор безпечно притиснуто до землі при старті.\n\n");

    /* 3. Дискретне керування навантаженням (ON / OFF) */
    printf("--- Крок 1: Дискретна комутування навантаження (ON / OFF) ---\n");

    printf("1.1. Повне ввімкнення навантаження (100%% duty / High GPIO):\n");
    mosfet_set_state(&mosfet, true);
    print_mosfet_status(&mosfet, "Full ON");

    printf("\n1.2. Повне вимкнення навантаження (0%% duty / Safe Pull-Down):\n");
    mosfet_set_state(&mosfet, false);
    print_mosfet_status(&mosfet, "Full OFF");

    /* 4. Плавне ШІМ-регулювання потужності навантаження */
    printf("\n--- Крок 2: Плавне ШІМ-регулювання потужності навантаження ---\n");
    uint8_t steps[] = {20, 40, 60, 80, 100};
    for (size_t i = 0; i < sizeof(steps)/sizeof(steps[0]); i++) {
        printf("2.%d. Встановлення скважності ШІМ: %u%%\n", (int)(i + 1), steps[i]);
        mosfet_set_duty(&mosfet, steps[i]);
        print_mosfet_status(&mosfet, "PWM Duty");
    }

    /* 5. Безпечна зупинка та притиснення затвора */
    printf("\n--- Крок 3: Безпечне вимкнення силового ключа наприкінці роботи ---\n");
    mosfet_safe_shutdown(&mosfet);
    print_mosfet_status(&mosfet, "Shutdown");

    printf("\n=== Демонстрацію завершено успішно ===\n");
    return 0;
}
