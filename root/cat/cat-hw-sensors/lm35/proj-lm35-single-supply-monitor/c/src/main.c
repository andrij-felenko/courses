/**
 * @file main.c
 * @brief Приклад практичного використання C-драйвера LM35DZ у мікроконтролерній системі.
 *
 * Демонструє ініціалізацію АЦП з внутрішньою опорною напругою 1.1 В, періодичне
 * зчитування миттєвих вибірок, їх згладжування за допомогою алгоритму EMA
 * та трансляцію відфільтрованої телеметрії через послідовний інтерфейс UART.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "lm35.h"

/**
 * @brief Симуляція передачі текстового рядка через послідовний інтерфейс UART.
 *
 * @param message Текстовий рядок телеметрії.
 */
static void uart_send_string(const char *message)
{
    /* В реальній системі тут викликається функція передачі UART (наприклад, uart_puts або HAL_UART_Transmit) */
    printf("%s", message);
}

int main(void)
{
    uart_send_string("=== Системний моніторинг температури (LM35DZ + EMA Filter) ===\r\n");

    /* 1. Налаштування конфігурації драйвера LM35DZ */
    lm35_config_t lm35_cfg = {
        .adc_channel   = 0,                   /* Канал АЦП 0 (ADC0) */
        .vref_mv       = LM35_ADC_VREF_MV,    /* Внутрішнє джерело опорної напруги 1.1 В (1100 мВ) */
        .default_alpha = LM35_EMA_ALPHA_DEFAULT /* Коефіцієнт EMA alpha = 0.15 */
    };

    /* 2. Ініціалізація периферії АЦП та драйвера */
    lm35_err_t status = lm35_init(&lm35_cfg);
    if (status != LM35_OK) {
        uart_send_string("[ПОМИЛКА] Спроба ініціалізації АЦП завершилася невдачею!\r\n");
        return -1;
    }
    uart_send_string("[ІНФО] АЦП конфігуровано: Vref = 1.1V (1100 мВ), Розрядність = 10 біт.\r\n");

    /* 3. Ініціалізація структури стану експоненціального фільтра */
    lm35_filter_t temp_filter;
    if (lm35_filter_init(&temp_filter, 0.15f) != LM35_OK) {
        uart_send_string("[ПОМИЛКА] Некоректні параметри EMA-фільтра!\r\n");
        return -1;
    }
    uart_send_string("[ІНФО] Потоковий EMA-фільтр підготовлено (alpha = 0.15).\r\n\r\n");

    /* 4. Симуляційний цикл оновлення даних та придушення високочастотного шуму */
    /* Масив симульованих кодів АЦП (базовий рівень ~233 (25.0 °C) із додаванням зашумлення та високочастотного викиду) */
    const uint16_t adc_samples[] = {
        233, /* 25.02 °C (початковий стан) */
        236, /* 25.35 °C */
        231, /* 24.81 °C */
        235, /* 25.24 °C */
        280, /* 30.07 °C - короткочасна шумова перешкода (спайк) */
        234, /* 25.13 °C */
        233, /* 25.02 °C */
        232, /* 24.92 °C */
        235, /* 25.24 °C */
        234  /* 25.13 °C */
    };
    const size_t sample_count = sizeof(adc_samples) / sizeof(adc_samples[0]);

    char uart_buffer[128];
    uint32_t timestamp_ms = 0;

    for (size_t i = 0; i < sample_count; i++) {
        uint16_t raw_adc = adc_samples[i];
        float voltage_mv = lm35_raw_to_voltage_mv(raw_adc, lm35_cfg.vref_mv);
        float instant_temp = lm35_voltage_to_temp_c(voltage_mv);
        float filtered_temp = lm35_filter_update(&temp_filter, instant_temp);

        snprintf(uart_buffer, sizeof(uart_buffer),
                 "[UART TX] Час: %4lu мс | АЦП: %4u | Напруга: %6.2f мВ | Миттєва: %5.2f °C | EMA-Фільтр: %5.2f °C\r\n",
                 (unsigned long)timestamp_ms,
                 raw_adc,
                 voltage_mv,
                 instant_temp,
                 filtered_temp);

        uart_send_string(uart_buffer);
        timestamp_ms += 100; /* Імітація періоду опитування 100 мс */
    }

    uart_send_string("\r\n=== Цикл моніторингу успішно завершено ===\r\n");
    return 0;
}
