#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

/* Апаратні піни керування реле */
#define PIN_RELAY_CHARGE     2
#define PIN_RELAY_DISCHARGE  3

/* Таймінги стандарту MIL-PRF-19978D (у мілісекундах) */
#define TIME_CHARGE_MS       (15 * 60 * 1000UL) /* 15 хвилин */
#define TIME_DISCHARGE_MS    (5 * 1000UL)        /* 5 секунд */
#define TIME_RECOVER_MS      (60 * 1000UL)       /* 1 хвилина */

/* Прототипи низькорівневих апаратних функцій платформи */
extern void gpio_write(uint8_t pin, bool state);
extern void delay_ms(uint32_t ms);
extern uint32_t get_time_ms(void);
extern float read_adc_voltage(void);

typedef struct {
    float v_charge;
    float v_recovered;
    float da_percent;
    bool success;
} da_result_t;

/* Виконання повного стандартизованого циклу вимірювання */
da_result_t measure_dielectric_absorption(void) {
    da_result_t res = {0.0f, 0.0f, 0.0f, false};

    /* Крок 0: Початкове знеструмлення всіх реле */
    gpio_write(PIN_RELAY_CHARGE, false);
    gpio_write(PIN_RELAY_DISCHARGE, false);
    delay_ms(100);

    /* Крок 1: Заряджання (15 хвилин) */
    gpio_write(PIN_RELAY_CHARGE, true);
    printf("Фаза 1: Заряджання конденсатора (15 хв)...\r\n");

    /* Очікування з періодичним виводом прогресу кожні 60 секунд */
    for (uint32_t min = 0; min < 15; min++) {
        delay_ms(60000UL);
        printf("  ...пройшло %lu хв, напруга: %.3f В\r\n", min + 1, read_adc_voltage());
    }

    /* Фіксація точної напруги заряду перед відключенням */
    res.v_charge = read_adc_voltage();
    if (res.v_charge < 1.0f) {
        printf("Помилка: відсутня напруга джерела заряду!\r\n");
        gpio_write(PIN_RELAY_CHARGE, false);
        return res;
    }

    /* Крок 2: Розряджання (рівно 5 секунд) */
    gpio_write(PIN_RELAY_CHARGE, false);
    delay_ms(10); /* Захисний захист від перекриття контактів (Break-before-make) */
    gpio_write(PIN_RELAY_DISCHARGE, true);
    printf("Фаза 2: Розряджання через 5 Ом (5 с)...\r\n");
    delay_ms(TIME_DISCHARGE_MS);

    /* Крок 3: Розімкнення та вистоювання (рівно 60 секунд) */
    gpio_write(PIN_RELAY_DISCHARGE, false);
    printf("Фаза 3: Вимірювання відновлення заряду (60 с)...\r\n");

    uint32_t start_time = get_time_ms();
    while ((get_time_ms() - start_time) < TIME_RECOVER_MS) {
        delay_ms(5000); /* Логування кожні 5 секунд */
        uint32_t elapsed = (get_time_ms() - start_time) / 1000;
        printf("  t = %lu с: V_rec = %.4f В\r\n", elapsed, read_adc_voltage());
    }

    /* Фінальний вимір напруги через 60 секунд */
    res.v_recovered = read_adc_voltage();

    /* Крок 4: Розрахунок відсотка діелектричної абсорбції */
    res.da_percent = (res.v_recovered / res.v_charge) * 100.0f;
    res.success = true;

    printf("\r\n=== РЕЗУЛЬТАТ ВИМІРЮВАННЯ ===\r\n");
    printf("V_charge    = %.3f В\r\n", res.v_charge);
    printf("V_recovered = %.5f В (%.2f мВ)\r\n", res.v_recovered, res.v_recovered * 1000.0f);
    printf("DA          = %.4f %%\r\n", res.da_percent);

    return res;
}
