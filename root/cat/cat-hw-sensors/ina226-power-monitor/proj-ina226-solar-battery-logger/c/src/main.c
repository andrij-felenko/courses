#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "ina226.h"
#include "power_monitor.h"

/**
 * @file main.c
 * @brief Практичний приклад застосування C-драйвера INA226 та модуля накопичення енергії.
 *
 * Демонструє ініціалізацію I2C шини, конфігурування давача INA226 з 10 мОм шунтом,
 * роботу апаратного таймера опитування та перехід MCU у сплячий режим для збереження енергії.
 */

/* --- Емуляція апаратного I2C для демонстрації --- */
static uint16_t g_mock_registers[256];

static ina226_err_t mock_i2c_write(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, uint16_t len)
{
    (void)dev_addr;
    if (len != 2 || data == NULL) return INA226_ERR_I2C;
    g_mock_registers[reg_addr] = (uint16_t)(((uint16_t)data[0] << 8) | data[1]);
    return INA226_OK;
}

static ina226_err_t mock_i2c_read(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len)
{
    (void)dev_addr;
    if (len != 2 || data == NULL) return INA226_ERR_I2C;

    uint16_t val = g_mock_registers[reg_addr];
    data[0] = (uint8_t)((val >> 8) & 0xFF);
    data[1] = (uint8_t)(val & 0xFF);
    return INA226_OK;
}

static void init_mock_hardware(void)
{
    /* Ініціалізація регістрів ідентифікації пристрою INA226 */
    g_mock_registers[INA226_REG_MANUFACTURER_ID] = INA226_MANUFACTURER_ID_VAL;
    g_mock_registers[INA226_REG_DIE_ID]          = INA226_DIE_ID_VAL;

    /*
     * Тестові показання пристрою під навантаженням:
     * Vbus = 12.0 В -> raw = 12.0 / 0.00125 = 9600 (0x2580)
     * Vshunt = 25 мВ -> raw = 0.025 / 0.0000025 = 10000 (0x2710)
     * Current = 2.5 А (при LSB = 10.0 / 32768 = 0.00030517578 A/LSB) -> raw ≈ 8192 (0x2000)
     * Power = 30.0 Вт -> raw = 30.0 / (25 * Current_LSB) ≈ 3932 (0x0F5C)
     */
    g_mock_registers[INA226_REG_BUS_VOLTAGE]   = 9600;
    g_mock_registers[INA226_REG_SHUNT_VOLTAGE] = 10000;
    g_mock_registers[INA226_REG_CURRENT]       = 8192;
    g_mock_registers[INA226_REG_POWER]         = 3932;
}

int main(void)
{
    printf("=== Запуск системи моніторингу живлення INA226 ===\n");

    /* Крок 1: Ініціалізація апаратної периферії I2C */
    init_mock_hardware();

    /* Крок 2: Формування структури конфігурації INA226 */
    power_monitor_config_t pm_config = {
        .sensor_config = {
            .i2c_addr = INA226_I2C_ADDR_DEFAULT,
            .r_shunt_ohms = 0.01f,           /* Вимірювальний шунт 10 мОм (0.01 Ом) */
            .max_expected_current_a = 10.0f, /* Максимальний очікуваний струм 10 А */
            .avg_mode = INA226_AVG_16,       /* Усереднення по 16 вибірках */
            .vbus_ct = INA226_CONV_TIME_1100US, /* Час перетворення VBUS 1.1 мс */
            .vsh_ct = INA226_CONV_TIME_1100US,  /* Час перетворення VSH 1.1 мс */
            .mode = INA226_MODE_SHUNT_BUS_CONT, /* Безперервний режим АЦП */
            .i2c_write = mock_i2c_write,
            .i2c_read = mock_i2c_read
        },
        .sample_interval_ms = 1000 /* Період опитування давача — 1 секунда */
    };

    /* Крок 3: Ініціалізація модуля моніторингу живлення */
    ina226_err_t err = power_monitor_init(&pm_config);
    if (err != INA226_OK) {
        printf("Помилка ініціалізації монітора живлення: код %d\n", err);
        return 1;
    }

    printf("INA226 успішно ініціалізовано та відкалібровано.\n");
    printf("Старт циклу моніторингу з переходом MCU у сплячий режим (Sleep Mode)...\n\n");

    /* Цикл симуляції роботи системи (10 періодів опитування по 1 сек) */
    for (int cycle = 1; cycle <= 10; ++cycle) {
        /*
         * Перехід мікроконтролера у сплячий режим для економії живлення.
         * MCU пробуджується апаратним перериванням таймера.
         */
        power_monitor_enter_sleep();

        /* Симуляція спрацьовування таймера та виклика обробника ISR */
        power_monitor_timer_isr_handler();

        /* Зчитування миттєвих показань давача */
        ina226_data_t instant_data;
        if (power_monitor_read_instantaneous(&instant_data) == INA226_OK) {
            printf("[Цикл %2d] Напруга: %6.3f В | Струм: %5.3f А | Потужність: %6.3f Вт\n",
                   cycle, instant_data.bus_voltage_v, instant_data.current_a, instant_data.power_w);
        }

        /* Періодичне виведення накопичених підсумків ємності та енергії */
        if (cycle % 2 == 0) {
            energy_accumulator_t acc;
            power_monitor_get_accumulator(&acc);

            printf("           --> Накопичено: %8.6f А·год | %8.6f Вт·год | Uptime: %.1f с (Вибірок: %llu)\n\n",
                   acc.total_ah, acc.total_wh, acc.uptime_seconds, (unsigned long long)acc.sample_count);
        }
    }

    printf("=== Моніторинг успішно завершено ===\n");
    return 0;
}
