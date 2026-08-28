/* Базовий алгоритм сканування шини I2C (STM32 HAL / C) */
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

void scan_i2c_bus(void) {
    printf("\r\n--- Початок сканування I2C шини ---\r\n");
    uint8_t devices_found = 0;

    for (uint8_t addr_7bit = 0x08; addr_7bit <= 0x77; ++addr_7bit) {
        /* Формуємо 8-бітну адресу для запису, як вимагає STM32 HAL */
        uint16_t dev_addr = (uint16_t)(addr_7bit << 1);

        /* Спроба перевірки готовності пристрою (1 спроба, таймаут 5 мс) */
        /* HAL_I2C_IsDeviceReady відправляє START + dev_addr + перевіряє ACK */
        extern I2C_HandleTypeDef hi2c1;
        if (HAL_I2C_IsDeviceReady(&hi2c1, dev_addr, 1, 5) == HAL_OK) {
            printf("Знайдено пристрій! 7-біт: 0x%02X | 8-біт WR: 0x%02X\r\n", 
                   addr_7bit, (uint8_t)dev_addr);
            devices_found++;
        }
    }

    if (devices_found == 0) {
        printf("Жодного пристрою на шині не виявлено (перевірте живлення та Pull-up)!\r\n");
    } else {
        printf("Сканування завершено. Знайдено пристроїв: %u\r\n", devices_found);
    }
}
