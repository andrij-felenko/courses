#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "pwm_driver.h"

/**
 * @brief Симуляція системної затримки в мілісекундах.
 * На реальному мікроконтролері використовується HAL_Delay() або SysTick.
 */
static void delay_ms(uint32_t ms)
{
    /* Симуляція очікування таймера */
    (void)ms;
}

/**
 * @brief Функція плавного розгону або сповільнення двигуна (Soft Start / Ramp).
 * 
 * @param driver Вказівник на драйвер ШІМ.
 * @param target_duty Цільовий коефіцієнт заповнення у відсотках (0..100%).
 * @param step_delay_ms Крок затримки між змінами заповнення (мс).
 */
static void motor_ramp_speed(pwm_driver_t *driver, uint8_t target_duty, uint32_t step_delay_ms)
{
    uint8_t current = pwm_get_current_duty(driver);

    if (target_duty > PWM_DUTY_MAX_PERCENT) {
        target_duty = PWM_DUTY_MAX_PERCENT;
    }

    printf("   [DC MOTOR RAMP] Зміна швидкості: %u%% -> %u%%\n", current, target_duty);

    if (current < target_duty) {
        for (uint8_t d = current + 1; d <= target_duty; d++) {
            pwm_set_duty_cycle(driver, d);
            delay_ms(step_delay_ms);
        }
    } else if (current > target_duty) {
        for (int16_t d = (int16_t)current - 1; d >= (int16_t)target_duty; d--) {
            pwm_set_duty_cycle(driver, (uint8_t)d);
            delay_ms(step_delay_ms);
        }
    }

    printf("   [DC MOTOR RAMP] Досягнуто встановлену швидкість: %u%%\n", pwm_get_current_duty(driver));
}

int main(void)
{
    printf("==================================================================\n");
    printf("  Схемотехніка та програмування низькостороннього MOSFET-ключа  \n");
    printf("==================================================================\n\n");

    printf("Опис схемотехнічного рішення:\n");
    printf("1. Навантаження (DC-мотор) підключено між +V_Supply та Drain N-MOSFET.\n");
    printf("2. Source N-MOSFET підключено до загальної шини (GND).\n");
    printf("3. Зворотний діод (Flyback diode) підключено паралельно мотору (катод до +V, анод до Drain),\n");
    printf("   що захищає MOSFET від сплесків ЕРС самоіндукції при закритті ключа.\n");
    printf("4. Резистор затвора R_g (10-100 Ом) обмежить піковий струм перезаряду ємності C_iss.\n");
    printf("5. Підтягувальний резистор R_pd (10 кОм) між Gate та GND забезпечує закритий стан\n");
    printf("   ключа під час скидання або ініціалізації мікроконтролера.\n\n");

    /* 1. Конфігурація периферійного таймера для ШІМ 20 кГц на частоті ядра 72 МГц */
    pwm_config_t config = {
        .timer_clock_hz = 72000000U,  // 72 МГц системна частота
        .pwm_frequency_hz = 20000U,   // 20 кГц ШІМ (поза межами чутного діапазону)
        .timer_channel = 1U,          // Канал 1
        .gpio_pin = 8U                // Вивід GPIO (наприклад, PB0 / TIM1_CH1)
    };

    pwm_driver_t driver;

    /* 2. Ініціалізація драйвера */
    if (pwm_driver_init(&driver, &config) != PWM_STATUS_OK) {
        printf("[ПОМИЛКА] Помилка ініціалізації драйвера ШІМ!\n");
        return 1;
    }

    /* 3. Запуск генерації ШІМ */
    if (pwm_driver_start(&driver) != PWM_STATUS_OK) {
        printf("[ПОМИЛКА] Помилка запуску апаратного таймера!\n");
        return 1;
    }

    printf("\n--- Початок виконання алгоритму керування DC-мотором ---\n\n");

    /* Крок A: Плавний пуск (Soft-Start) від 0% до 100% заповнення */
    printf("Тест 1: Плавний розгін двигуна (Soft Start 0%% -> 100%%)\n");
    motor_ramp_speed(&driver, 100, 20);
    delay_ms(1000);

    /* Крок B: Плавне зменшення обертів до крейсерської швидкості (50%) */
    printf("\nТест 2: Зниження швидкості до 50%%\n");
    motor_ramp_speed(&driver, 50, 15);
    delay_ms(1000);

    /* Крок C: Дискретне перемикання ступенів швидкості (25%, 75%, 10%) */
    printf("\nТест 3: Перевірка роботи на різних ступенях потужності\n");
    
    printf("-> Встановлення 25%% потужності\n");
    pwm_set_duty_cycle(&driver, 25);
    printf("   Поточний заповнення: %u%%\n", pwm_get_current_duty(&driver));
    delay_ms(500);

    printf("-> Встановлення 75%% потужності\n");
    pwm_set_duty_cycle(&driver, 75);
    printf("   Поточний заповнення: %u%%\n", pwm_get_current_duty(&driver));
    delay_ms(500);

    printf("-> Встановлення 10%% потужності\n");
    pwm_set_duty_cycle(&driver, 10);
    printf("   Поточний заповнення: %u%%\n", pwm_get_current_duty(&driver));
    delay_ms(500);

    /* Крок D: Плавне повне зупинення та вимкнення ключа */
    printf("\nТест 4: Плавне зупинення мотора (Ramp Down 10%% -> 0%%)\n");
    motor_ramp_speed(&driver, 0, 25);

    /* 4. Зупинка таймера та безпечна деініціалізація */
    printf("\n--- Вимкнення периферії ---\n");
    pwm_driver_stop(&driver);

    printf("\nДемонстрацію успішно завершено.\n");
    return 0;
}
