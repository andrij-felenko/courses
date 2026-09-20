#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "moc3063.h"

/* Номер GPIO виводу мікроконтролера, підключеного до вхідного світлодіода MOC3063 */
#define TRIAC_CTRL_PIN 4

/**
 * @brief Симуляція апаратного рівня запису значення у вивід GPIO.
 * 
 * У реальній системі на базі STM32, ESP32, AVR чи PIC ця функція 
 * обгортає виклики типу HAL_GPIO_WritePin(), gpio_set_level() або PORTx.
 * 
 * @param pin Номер GPIO виводу.
 * @param level Логічний рівень (true = HIGH, false = LOW).
 */
static void mcu_gpio_write(uint8_t pin, bool level)
{
    printf("[GPIO HW] Вивід GPIO_%u -> %s (%s)\n", 
           pin, 
           level ? "HIGH (1)" : "LOW (0)",
           level ? "Світлодіод оптопари заживлено" : "Світлодіод оптопари знеструмлено");
}

/**
 * @brief Симуляція затримки мікроконтролера в мілісекундах.
 * 
 * @param ms Тривалість затримки в мілісекундах.
 */
static void mcu_delay_ms(uint32_t ms)
{
    printf("   [Таймер] Затримка %u мс...\n", (unsigned int)ms);
}

/**
 * @brief Допоміжна функція друку поточного логічного стану драйвера.
 * 
 * @param driver Вказівник на дескриптор MOC3063.
 */
static void print_triac_status(const moc3063_t *driver)
{
    moc3063_state_t state;
    if (moc3063_get_state(driver, &state) == MOC3063_OK) {
        printf(" -> Логічний стан навантаження: %s\n", 
               (state == MOC3063_STATE_ON) ? "УВІМКНЕНО (ON)" : "ВИМКНЕНО (OFF)");
    } else {
        printf(" -> Помилка зчитування стану драйвера!\n");
    }
}

int main(void)
{
    printf("=== Керування силовим симістором через оптопару MOC3063 з Zero-Cross ===\n\n");

    /* 
     * Фізичний принцип роботи MOC3063:
     * - MOC3063 містить внутрішній оптично ізольований IR-світлодіод та фотосимістор 
     *   із вбудованою апаратною схемою виявлення переходу через нуль (Zero-Crossing Detector).
     * - Коли МК подає струм на світлодіод (стан ON), внутрішній фотосимістор чекає, 
     *   поки напруга мережі 220V/110V AC наблизиться до 0V (в межах ±5...20В).
     * - Після переходу через нуль детектор дозволяє відкритися фотосимістору, який 
     *   відкриває головний силовий симістор (наприклад, BTA16). Це запобігає 
     *   пусковим кидкам струму та випромінюванню завад (EMI).
     * - Програмі на МК не потрібно відстежувати переривання Zero-Cross — MOC3063 робить це апаратно.
     */

    /* 1. Конфігурація драйвера MOC3063 */
    moc3063_config_t config = {
        .gpio_pin = TRIAC_CTRL_PIN,
        .active_level = MOC3063_ACTIVE_HIGH, /* Active HIGH: HIGH відкриває оптопару */
        .initial_state = MOC3063_STATE_OFF,  /* Початковий безпечний стан: вимкнено */
        .gpio_write = mcu_gpio_write
    };

    moc3063_t triac_driver;

    /* 2. Безпечна ініціалізація драйвера */
    printf("1. Ініціалізація драйвера MOC3063...\n");
    moc3063_status_t status = moc3063_init(&triac_driver, &config);
    if (status != MOC3063_OK) {
        printf("Помилка ініціалізації драйвера MOC3063 (код %d)!\n", status);
        return 1;
    }
    printf("Драйвер успішно ініціалізовано.\n");
    print_triac_status(&triac_driver);
    printf("\n");

    /* 3. Увімкнення мережевого навантаження */
    printf("2. Подача сигналу на увімкнення навантаження (MOC3063_STATE_ON):\n");
    moc3063_turn_on(&triac_driver);
    print_triac_status(&triac_driver);
    printf("   [Примітка] Силовий симістор відкриється в момент найближчого переходу AC напруги через нуль (<10 мс).\n");
    mcu_delay_ms(1000);
    printf("\n");

    /* 4. Перемикання стану навантаження (Toggle) */
    printf("3. Перемикання стану навантаження (Toggle -> OFF):\n");
    moc3063_toggle(&triac_driver);
    print_triac_status(&triac_driver);
    printf("   [Примітка] Силовий симістор закриється при переході струму навантаження через нуль.\n");
    mcu_delay_ms(1000);
    printf("\n");

    /* 5. Повторне увімкнення та вимкнення */
    printf("4. Повторне увімкнення (turn_on):\n");
    moc3063_turn_on(&triac_driver);
    print_triac_status(&triac_driver);
    mcu_delay_ms(500);

    printf("\n5. Безпечне вимкнення навантаження (turn_off):\n");
    moc3063_turn_off(&triac_driver);
    print_triac_status(&triac_driver);
    mcu_delay_ms(500);

    printf("\n=== Демонстрацію комутації через MOC3063 завершено успішно ===\n");
    return 0;
}
