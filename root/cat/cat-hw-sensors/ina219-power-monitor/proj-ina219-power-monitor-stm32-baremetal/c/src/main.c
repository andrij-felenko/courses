#include "../include/ina219.h"
#include "../include/i2c_driver.h"
#include <stdio.h>
#include <string.h>

/**
 * @file main.c
 * @brief Приклад практичного використання C-драйвера INA219 на мікроконтролері STM32.
 */

/* Макетні адреси регістрів периферії STM32 для демонстрації без зовнішніх залежностей */
#define STM32_I2C1_BASE  ((i2c_reg_t *)0x40005400U)

/* Простий апаратний макет UART для телеметрії */
static void uart_init(uint32_t baudrate) {
    (void)baudrate;
    /* Ініціалізація тактування GPIO та USART1 у справжньому системному проєкті */
}

static void uart_send_string(const char *str) {
    if (!str) return;
    while (*str) {
        /* В реальному STM32: чекаємо USART1->SR & USART_SR_TXE і пишемо USART1->DR = *str */
        (void)*str++;
    }
}

/**
 * @brief Проста функція затримки для опитування пристрою.
 */
static void delay_ms(uint32_t ms) {
    for (volatile uint32_t i = 0; i < ms * 8000U; i++) {
        __asm__("nop");
    }
}

int main(void) {
    /* 1. Ініціалізація UART для телеметричного виводу */
    uart_init(115200);
    uart_send_string("=== INA219 Bare-Metal STM32 Power Monitor Driver ===\r\n");

    /* 2. Ініціалізація шини I2C1 (APB1 = 16 МГц, SCL = 100 кГц) */
    i2c_bus_t i2c1_bus;
    i2c_status_t i2c_status = i2c_init(&i2c1_bus, STM32_I2C1_BASE, 16000000U, 100000U);
    if (i2c_status != I2C_OK) {
        uart_send_string("ERROR: Failed to initialize I2C bus peripheral!\r\n");
        return -1;
    }

    /* 3. Конфігурація монітора INA219:
     * - Адреса: 0x40 (A0=GND, A1=GND)
     * - Шкала шини: 32 В
     * - PGA: ±320 мВ (підсилення /8)
     * - АЦП: Усереднення по 16 вибірках (8.51 мс на вимірювання)
     * - Режим: Безперервний моніторинг шини та шунта
     * - Шунт: R_shunt = 0.1 Ом (100 мОм)
     * - Максимальний очікуваний струм: 2.0 А
     */
    ina219_config_t config = {
        .i2c_addr = INA219_I2C_ADDR_DEFAULT,
        .bus_range = INA219_BUS_RANGE_32V,
        .pga_gain = INA219_PGA_GAIN_8_320MV,
        .bus_adc = INA219_ADC_AVG_16,
        .shunt_adc = INA219_ADC_AVG_16,
        .mode = INA219_MODE_SHUNT_BUS_CONTINUOUS,
        .r_shunt_ohms = 0.1f,
        .max_expected_i = 2.0f
    };

    ina219_t ina219;
    i2c_status = ina219_init(&ina219, &i2c1_bus, &config);
    if (i2c_status != I2C_OK) {
        uart_send_string("ERROR: INA219 initialization or calibration failed!\r\n");
        return -2;
    }

    uart_send_string("INA219 initialized and calibrated successfully.\r\n");

    ina219_data_t telemetry;
    char uart_buffer[128];

    /* 4. Головний вимірювальний цикл опитування давача */
    while (1) {
        i2c_status = ina219_read_telemetry(&ina219, &telemetry);
        if (i2c_status == I2C_OK) {
            /* Контроль прапорця готовності CNVR та переповнення OVF */
            if (!telemetry.conversion_ready) {
                uart_send_string("[WARN] CNVR: ADC conversion not ready yet.\r\n");
            } else if (telemetry.math_overflow) {
                uart_send_string("[ALERT] OVF: Internal math overflow detected! Current/Power invalid.\r\n");
            } else {
                /* Формуємо асинхронний телеметричний кадр для UART */
                snprintf(uart_buffer, sizeof(uart_buffer),
                         "[TELEMETRY] Bus: %.3f V | Shunt: %.2f mV | Current: %.2f mA | Power: %.2f mW\r\n",
                         telemetry.voltage_v,
                         telemetry.shunt_voltage_mv,
                         telemetry.current_ma,
                         telemetry.power_mw);

                uart_send_string(uart_buffer);
            }
        } else {
            uart_send_string("ERROR: I2C read failure during telemetry update!\r\n");
        }

        /* Періодичність опитування 500 мс */
        delay_ms(500);
    }

    return 0;
}
