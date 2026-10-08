/**
 * @file main.c
 * @brief Приклад реального використання C-драйвера масиву VL53L0X у вбудованій системі.
 *
 * Демонструє послідовну розконсервацію ліній XSHUT, перепризначення 4 унікальних I2C-адрес,
 * налаштування апаратних переривань EXTI та побудову неблокуючого суперциклу обробки
 * лазерних далекомірів у реальному часі.
 */

#include <stdio.h>
#include "vl53l0x_array.h"

/* Зовнішній функціонал модуля EXTI */
extern void exti_handler_register_array(VL53L0X_Array_t *arr);
extern bool exti_pop_pending_sensor(uint8_t *p_sensor_idx, uint32_t *p_timestamp);

/* Імітація апаратного інтерфейсу I2C та GPIO для автономної збірки прикладу */
static uint32_t g_system_ticks = 0;

hal_status_t hal_i2c_init(uint32_t speed_hz) { (void)speed_hz; return HAL_I2C_OK; }
hal_status_t hal_i2c_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t value) { (void)dev_addr; (void)reg_addr; (void)value; return HAL_I2C_OK; }
hal_status_t hal_i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *p_value) {
    (void)dev_addr;
    if (reg_addr == VL53L0X_REG_IDENTIFICATION_MODEL_ID) {
        *p_value = VL53L0X_EXPECTED_DEVICE_ID;
    } else {
        *p_value = 0x00;
    }
    return HAL_I2C_OK;
}
hal_status_t hal_i2c_write_multi(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *p_data, uint16_t len) { (void)dev_addr; (void)reg_addr; (void)p_data; (void)len; return HAL_I2C_OK; }
hal_status_t hal_i2c_read_multi(uint8_t dev_addr, uint8_t reg_addr, uint8_t *p_data, uint16_t len) {
    (void)dev_addr; (void)reg_addr;
    for (uint16_t i = 0; i < len; i++) p_data[i] = 0;
    /* Симуляція статусу OK та відстані 250 мм у байтах 10 та 11 */
    if (len >= 12) {
        p_data[0] = (0 << 3); /* Valid status */
        p_data[10] = 0x00;
        p_data[11] = 0xFA;    /* 250 мм */
    }
    return HAL_I2C_OK;
}
void hal_gpio_write(hal_gpio_pin_t pin, bool state) { (void)pin; (void)state; }
void hal_delay_ms(uint32_t ms) { g_system_ticks += ms; }
uint32_t hal_get_tick_ms(void) { return g_system_ticks; }

/* ========================================================================== */
/*                             ГОЛОВНА ПРОГРАМА                               */
/* ========================================================================== */

int main(void)
{
    printf("=== Ініціалізація масиву лазерних ToF-давачів VL53L0X ===\n");

    /* 1. Ініціалізація апаратного інтерфейсу I2C (400 кГц Fast Mode) */
    if (hal_i2c_init(400000) != HAL_I2C_OK) {
        printf("Помилка: не вдалося ініціалізувати периферичний модуль I2C!\n");
        return -1;
    }

    /* 2. Конфігурація апаратних виводів для 4 давачів */
    VL53L0X_Array_t sensor_array;
    const uint8_t target_i2c_addresses[4] = { 0x30, 0x31, 0x32, 0x33 };

    for (uint8_t i = 0; i < 4; i++) {
        /* Призначаємо лінії XSHUT на PORTA (pins 0..3) */
        sensor_array.dev[i].xshut_pin.port_base = 0x40020000U;
        sensor_array.dev[i].xshut_pin.pin_id = (1U << i);

        /* Призначаємо лінії переривань INT (EXTI) на PORTB (pins 0..3) */
        sensor_array.dev[i].exti_pin.port_base = 0x40020400U;
        sensor_array.dev[i].exti_pin.pin_id = (1U << i);
    }

    /* 3. Запуск алгоритму послідовного виведення з Hardware Shutdown та переадресації */
    vl53l0x_err_t status = vl53l0x_array_init(&sensor_array, target_i2c_addresses, 4);
    if (status != VL53L0X_OK) {
        printf("Критичний збій ініціалізації масиву VL53L0X! Код помилки: %d\n", status);
        return -1;
    }

    printf("Успішно перепризначено I2C-адреси для 4 сенсорів [0x30, 0x31, 0x32, 0x33].\n");

    /* 4. Реєстрація масиву в модулі обробки переривань EXTI */
    exti_handler_register_array(&sensor_array);

    /* 5. Запуск режиму безперервного вимірювання (Continuous Mode) для всіх давачів */
    for (uint8_t i = 0; i < sensor_array.count; i++) {
        if (vl53l0x_start_continuous(&sensor_array.dev[i]) != VL53L0X_OK) {
            printf("Не вдалося запустити Continuous Mode для сенсора #%d\n", i);
        }
    }

    printf("Усі далекоміри переведено в режим Continuous Ranging. Запуск суперциклу.\n");

    /* Симуляція спрацьовування апаратного переривання від сенсора #0 */
    extern void HAL_GPIO_EXTI_Callback(uint16_t pin_id);
    HAL_GPIO_EXTI_Callback(sensor_array.dev[0].exti_pin.pin_id);

    /* 6. Основний неблокуючий суперцикл обробки подій у реальному часі */
    uint32_t last_heartbeat = hal_get_tick_ms();
    uint32_t loop_iterations = 0;

    while (loop_iterations < 10) {
        loop_iterations++;
        uint8_t active_sensor_idx = 0;
        uint32_t event_time = 0;

        /* Вилучення подій переривання з черги без блокування виконання */
        if (exti_pop_pending_sensor(&active_sensor_idx, &event_time)) {
            vl53l0x_dev_t *dev = &sensor_array.dev[active_sensor_idx];
            uint16_t distance_mm = 0;

            /* Зчитування виміряної дистанції по шині I2C */
            if (vl53l0x_read_distance_async(dev, &distance_mm) == VL53L0X_OK) {
                printf("[t=%lu ms] Сенсор #%d (I2C: 0x%02X): Дистанція = %u мм (Статус: %u)\n",
                       (unsigned long)event_time,
                       dev->id,
                       dev->current_addr,
                       distance_mm,
                       dev->range_status);
            } else {
                printf("Помилка зчитування дистанції з сенсора #%d\n", dev->id);
            }
        }

        /* Симуляція паралельних неблокуючих системних задач (Heartbeat LED) */
        if (hal_get_tick_ms() - last_heartbeat >= 500) {
            last_heartbeat = hal_get_tick_ms();
            /* Toggle Heartbeat LED */
        }
    }

    printf("=== Завершення демонстраційного прогону суперциклу ===\n");
    return 0;
}
