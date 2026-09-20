#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "drv8833.h"

/* Симуляція затримки в мілісекундах для демонстраційного прикладу */
static void sys_delay_ms(uint32_t ms)
{
    /* На реальному МК тут викликається HAL_Delay(ms) або sys_tick delay */
    printf("   [Таймер] Затримка %u мс...\n", (unsigned int)ms);
}

/* Симуляція апаратного рівня записи логічного виводу GPIO */
static void mcu_gpio_write(uint8_t pin_id, bool state)
{
    printf("[GPIO HW] Вивід %u -> %s\n", pin_id, state ? "HIGH (1)" : "LOW (0)");
}

/* Симуляція апаратного рівня налаштування ШІМ генератора */
static void mcu_pwm_set_duty(uint8_t pwm_channel, uint8_t duty_percent)
{
    printf("[PWM  HW] Канал ШІМ %u -> Заповнення: %u%%\n", pwm_channel, duty_percent);
}

/* Конфігурація периферії МК (GPIO та генераторів ШІМ) */
static void mcu_peripherals_init(void)
{
    printf("--- Ініціалізація апаратної периферії МК (GPIO / TIM PWM) ---\n");
    /* У реальному проєкті тут здійснюється налаштування груп виводів GPIO та таймерів PWM */
}

/* Допоміжна функція виводу стану мотора в консоль */
static void print_motor_status(const drv8833_t *driver, drv8833_motor_id_t motor, const char *motor_name)
{
    drv8833_motor_state_t state;
    if (drv8833_get_motor_state(driver, motor, &state) == DRV8833_OK) {
        const char *mode_str = "НЕВІДОМО";
        switch (state.mode) {
        case DRV8833_MODE_COAST:   mode_str = "Вільний вибіг (COAST)"; break;
        case DRV8833_MODE_FORWARD: mode_str = "Вперед (FORWARD)"; break;
        case DRV8833_MODE_REVERSE: mode_str = "Назад (REVERSE)"; break;
        case DRV8833_MODE_BRAKE:   mode_str = "Активне гальмування (BRAKE)"; break;
        }
        printf(" -> Статус %s: Режим = %s, Швидкість = %u%%\n", motor_name, mode_str, state.speed_percent);
    }
}

int main(void)
{
    printf("=== Демонстрація керування моторами через DRV8833 ===\n\n");

    /* 1. Ініціалізація периферії мікроконтролера */
    mcu_peripherals_init();

    /* 2. Конфігурація виводів DRV8833 */
    drv8833_config_t config = {
        .motor_a = {
            .pin_in1 = 5,
            .pin_in2 = 6,
            .pwm_ch_in1 = 0, /* Канал ШІМ для IN1 */
            .pwm_ch_in2 = 1  /* Канал ШІМ для IN2 */
        },
        .motor_b = {
            .pin_in1 = 9,
            .pin_in2 = 10,
            .pwm_ch_in1 = 2, /* Канал ШІМ для IN3 */
            .pwm_ch_in2 = 3  /* Канал ШІМ для IN4 */
        },
        .pin_sleep = 4,      /* Вивід nSLEEP */
        .gpio_write = mcu_gpio_write,
        .pwm_set = mcu_pwm_set_duty
    };

    /* 3. Ініціалізація драйвера H-моста */
    drv8833_t driver;
    printf("\n--- Ініціалізація драйвера DRV8833 ---\n");
    if (drv8833_init(&driver, &config) != DRV8833_OK) {
        printf("Помилка ініціалізації DRV8833!\n");
        return 1;
    }
    printf("Драйвер успішно ініціалізовано.\n\n");

    /* 4. Виконання тестового циклу керування */

    /* Крок A: Плавний розгін мотора A вперед */
    printf("1. Плавний розгін мотора A в напрямку ВПЕРЕД:\n");
    for (uint8_t speed = 20; speed <= 100; speed += 20) {
        drv8833_set_motor(&driver, DRV8833_MOTOR_A, DRV8833_MODE_FORWARD, speed);
        print_motor_status(&driver, DRV8833_MOTOR_A, "Мотор A");
        sys_delay_ms(200);
    }

    /* Крок B: Запуск мотора B на половину потужності */
    printf("\n2. Синхронний запуск мотора B (50%% speed, ВПЕРЕД):\n");
    drv8833_set_motor(&driver, DRV8833_MOTOR_B, DRV8833_MODE_FORWARD, 50);
    print_motor_status(&driver, DRV8833_MOTOR_B, "Мотор B");
    sys_delay_ms(500);

    /* Крок C: Активне електродинамічне гальмування мотора A */
    printf("\n3. Активне гальмування (BRAKE) мотора A:\n");
    drv8833_brake(&driver, DRV8833_MOTOR_A);
    print_motor_status(&driver, DRV8833_MOTOR_A, "Мотор A");
    sys_delay_ms(500);

    /* Крок D: Реверс мотора B (рух назад зі швидкістю 75%) */
    printf("\n4. Перемикання напрямку руху мотора B (НАЗАД, 75%% speed):\n");
    drv8833_set_motor(&driver, DRV8833_MOTOR_B, DRV8833_MODE_REVERSE, 75);
    print_motor_status(&driver, DRV8833_MOTOR_B, "Мотор B");
    sys_delay_ms(500);

    /* Крок E: Зміна швидкості мотора B у поточному напрямку */
    printf("\n5. Плавне зниження швидкості мотора B до 30%%:\n");
    drv8833_set_speed(&driver, DRV8833_MOTOR_B, 30);
    print_motor_status(&driver, DRV8833_MOTOR_B, "Мотор B");
    sys_delay_ms(500);

    /* Крок F: Вільний вибіг мотора B */
    printf("\n6. Вільна зупинка (COAST) мотора B:\n");
    drv8833_coast(&driver, DRV8833_MOTOR_B);
    print_motor_status(&driver, DRV8833_MOTOR_B, "Мотор B");
    sys_delay_ms(300);

    /* Крок G: Переведення DRV8833 у режим сну для економії енергії */
    printf("\n7. Переведення DRV8833 у режим сну (nSLEEP = LOW):\n");
    drv8833_set_sleep(&driver, true);
    sys_delay_ms(500);

    /* Крок H: Пробудження зі сну та скидання у безпечний стан */
    printf("\n8. Пробудження DRV8833 зі сну (nSLEEP = HIGH):\n");
    drv8833_set_sleep(&driver, false);
    sys_delay_ms(200);

    printf("\n=== Демонстрацію завершено успішно ===\n");
    return 0;
}
