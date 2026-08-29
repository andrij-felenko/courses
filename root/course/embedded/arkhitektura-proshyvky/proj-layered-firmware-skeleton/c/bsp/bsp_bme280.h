// bsp/bsp_bme280.h — драйвер давача мікроклімату.
// Залежить ЛИШЕ від абстракції шини. Жодного вендорного stm32f4xx_hal.h тут бути не може:
// саме таке включення миттєво привʼязує драйвер до одного чипа.
#ifndef BSP_BME280_H
#define BSP_BME280_H

#include "hal/hal_i2c.h"

// Непрозорий дескриптор: поля структури невидимі поза файлом реалізації.
typedef struct bsp_bme280_dev bsp_bme280_t;

typedef struct {
    float temperature_c;
    float humidity_percent;
    float pressure_hpa;
} bsp_bme280_data_t;

// Статичне місце під дескриптор: клієнт оголошує цю структуру там, де йому зручно
// (глобально, у структурі застосунку, на стеку задачі), а драйвер обходиться без malloc.
typedef struct bsp_bme280_storage {
    union {
        uint8_t bytes[128];
        void* align_ptr;   // Вирівнювання під найсуворіший тип усередині
        uint32_t align_u32;
    } opaque;
} bsp_bme280_storage_t;

#define BSP_BME280_ADDR_PRIMARY 0x76u    // SDO до землі
#define BSP_BME280_ADDR_SECONDARY 0x77u  // SDO до живлення

// Повертає NULL, якщо шина мовчить або на адресі сидить не BME280.
bsp_bme280_t* bsp_bme280_init(bsp_bme280_storage_t* storage, hal_i2c_bus_t* bus, uint8_t i2c_addr);

// Повне переналаштування вже створеного дескриптора — потрібне після того,
// як службова політика перезапустила живлення лінії давачів.
bool bsp_bme280_reconfigure(bsp_bme280_t* dev);

// false означає «даних немає»: помилка шини або чип ще не встиг зробити вибірку.
// Сміттєві байти буфера в математику не потрапляють ніколи.
bool bsp_bme280_read(bsp_bme280_t* dev, bsp_bme280_data_t* out_data);

// Останній статус шини — для діагностики верхніх шарів.
hal_i2c_status_t bsp_bme280_last_status(const bsp_bme280_t* dev);

#endif  // BSP_BME280_H
