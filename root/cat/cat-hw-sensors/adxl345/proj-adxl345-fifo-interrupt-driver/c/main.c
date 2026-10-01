#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "adxl345.h"

/* ========================================================================= */
/*                   Імітація апаратного шинного HAL (I2C/SPI)                */
/* ========================================================================= */

/* Фіктивна пам'ять регістрів ADXL345 для демонстрації на будь-якому ПК */
static uint8_t g_mock_registers[0x40];

static int32_t hal_i2c_read(void *intf_ptr, uint8_t reg_addr, uint8_t *data, uint16_t len) {
    (void)intf_ptr;
    if (reg_addr + len > sizeof(g_mock_registers)) {
        return -1;
    }
    
    /* Якщо зчитуються регістри вихідних даних (0x32..0x37), згенеруємо тестове прискорення */
    if (reg_addr == ADXL345_REG_DATAX0 && len == 6) {
        /* Приклад: X = 0.5g (128 МЗР), Y = -0.25g (-64 МЗР), Z = 1.0g (256 МЗР) */
        int16_t test_x = 128;
        int16_t test_y = -64;
        int16_t test_z = 256;

        data[0] = (uint8_t)(test_x & 0xFF);
        data[1] = (uint8_t)((test_x >> 8) & 0xFF);
        data[2] = (uint8_t)(test_y & 0xFF);
        data[3] = (uint8_t)((test_y >> 8) & 0xFF);
        data[4] = (uint8_t)(test_z & 0xFF);
        data[5] = (uint8_t)((test_z >> 8) & 0xFF);
        return 0;
    }

    memcpy(data, &g_mock_registers[reg_addr], len);
    return 0;
}

static int32_t hal_i2c_write(void *intf_ptr, uint8_t reg_addr, const uint8_t *data, uint16_t len) {
    (void)intf_ptr;
    if (reg_addr + len > sizeof(g_mock_registers)) {
        return -1;
    }
    memcpy(&g_mock_registers[reg_addr], data, len);
    return 0;
}

/* ========================================================================= */
/*                     Обробка апаратних переривань INT1/INT2                */
/* ========================================================================= */
static volatile bool g_int1_watermark_flag = false;
static volatile bool g_int2_overrun_flag   = false;

/* Обробник переривання лінії INT1 (маршрутизовано порогове заповнення Watermark) */
void GPIO_INT1_IRQHandler(void) {
    g_int1_watermark_flag = true;
}

/* Обробник переривання лінії INT2 (маршрутизовано аварійне переповнення Overrun) */
void GPIO_INT2_IRQHandler(void) {
    g_int2_overrun_flag = true;
}

/* ========================================================================= */
/*                              Головна програма                             */
/* ========================================================================= */

int main(void) {
    printf("=== ADXL345 3-Axis Accelerometer C Driver Demo ===\n\n");

    /* Підготовка імітації регістрів (повертаємо DEVID = 0xE5) */
    memset(g_mock_registers, 0, sizeof(g_mock_registers));
    g_mock_registers[ADXL345_REG_DEVID] = ADXL345_DEVICE_ID;

    /* 1. Ініціалізація структури апаратного інтерфейсу HAL */
    adxl345_hal_t hal = {
        .read     = hal_i2c_read,
        .write    = hal_i2c_write,
        .intf_ptr = NULL /* Може містити вказівник на I2C_HandleTypeDef в STM32 */
    };

    /* 2. Конфігурація акселерометра ADXL345 */
    adxl345_config_t config = {
        .odr               = ADXL345_ODR_100_HZ,              /* 100 Гц */
        .range             = ADXL345_RANGE_16G,               /* ±16g */
        .full_resolution   = true,                            /* 3.9 мг/МЗР */
        .fifo_mode         = ADXL345_FIFO_STREAM,             /* Потоковий буфер */
        .watermark_samples = 16,                              /* Порог Watermark: 16 кадрів */
        .int_enable_mask   = ADXL345_INT_WATERMARK | ADXL345_INT_OVERRUN,
        /* Watermark (біт 1) -> 0 (INT1), Overrun (біт 0) -> 1 (INT2) */
        .int_map_mask      = ADXL345_INT_OVERRUN
    };

    adxl345_dev_t dev;

    /* 3. Виклик функції ініціалізації драйвера */
    adxl345_status_t status = adxl345_init(&dev, &hal, &config);
    if (status != ADXL345_OK) {
        printf("[ПОМИЛКА] Ініціалізація ADXL345 не вдалася! Код: %d\n", status);
        return -1;
    }
    printf("[OK] ADXL345 успішно ініціалізовано. DEVID: 0x%02X\n", ADXL345_DEVICE_ID);
    printf("[OK] Режим вимірювання (Measurement Mode) активовано, ODR: 100 Гц, Stream FIFO: 16 вибірок.\n\n");

    /* Симуляція надходження апаратних переривань */
    GPIO_INT1_IRQHandler(); /* Імітація спрацювання INT1 (Watermark) */

    /* 4. Головний суперцикл обробки (Super-loop) */
    int loop_counter = 0;
    while (loop_counter < 3) {
        loop_counter++;

        /* Обробка аварійного переривання Overrun на лінії INT2 */
        if (g_int2_overrun_flag) {
            g_int2_overrun_flag = false;
            printf("[УВАГА! INT2] Виявлено переповнення FIFO (Overrun)! Очищення буфера...\n");
        }

        /* Обробка нормального переривання Watermark на лінії INT1 */
        if (g_int1_watermark_flag) {
            g_int1_watermark_flag = false;

            uint8_t int_src = 0;
            adxl345_read_int_source(&dev, &int_src);

            uint8_t samples_in_fifo = 0;
            adxl345_get_fifo_level(&dev, &samples_in_fifo);

            printf("[ПОДІЯ INT1] Зчитано джерело переривань INT_SOURCE: 0x%02X\n", int_src);
            printf("[INFO] Кількість кадрів у FIFO буфері: %d\n", samples_in_fifo);

            /* Зчитування кадру даних за допомогою атомарного burst-read */
            adxl345_raw_data_t raw;
            adxl345_accel_g_t accel;

            if (adxl345_read_raw(&dev, &raw) == ADXL345_OK) {
                adxl345_convert_raw_to_g(&raw, &accel);

                printf("  -> Сирі значення: X = %6d, Y = %6d, Z = %6d\n", raw.x, raw.y, raw.z);
                printf("  -> Прискорення:  X = %6.3fg, Y = %6.3fg, Z = %6.3fg\n\n",
                       accel.x, accel.y, accel.z);
            } else {
                printf("[ПОМИЛКА] Помилка зчитання даних по шині!\n");
            }
        }
    }

    printf("=== Демонстрацію роботи драйвера успішно завершено ===\n");
    return 0;
}
