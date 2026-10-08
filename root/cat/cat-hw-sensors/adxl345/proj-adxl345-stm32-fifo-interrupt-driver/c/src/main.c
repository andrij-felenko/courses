#include <stdio.h>
#include "adxl345.h"
#include "stm32_exti.h"

/* Симуляція низькорівневої транзакції I2C для демонстрації драйвера на STM32 */
static int32_t stm32_i2c_read(void *handle, uint8_t reg_addr, uint8_t *data, uint16_t len)
{
    (void)handle;

    /* У реальному проєкті STM32 використовується HAL_I2C_Mem_Read():
     * return (HAL_I2C_Mem_Read((I2C_HandleTypeDef*)handle, ADXL345_I2C_ADDR_ALT_LOW, 
     *                          reg_addr, I2C_MEMADD_SIZE_8BIT, data, len, 100) == HAL_OK) ? 0 : -1;
     */

    /* Демонстраційне повернення значень */
    if (reg_addr == ADXL345_REG_DEVID) {
        data[0] = ADXL345_DEVICE_ID;
    } else if (reg_addr == ADXL345_REG_FIFO_STATUS) {
        data[0] = 16U; /* 16 відліків за порогом Watermark */
    } else if (reg_addr == ADXL345_REG_INT_SOURCE) {
        data[0] = ADXL345_INT_WATERMARK;
    } else if (reg_addr == ADXL345_REG_DATAX0 && len >= 6) {
        /* Симуляція вимірювання 1g за віссю Z */
        data[0] = 0x00; data[1] = 0x00; /* X = 0 */
        data[2] = 0x00; data[3] = 0x00; /* Y = 0 */
        data[4] = 0x00; data[5] = 0x01; /* Z = 256 LSB (1.0g у Full-Res) */
    }
    return 0;
}

static int32_t stm32_i2c_write(void *handle, uint8_t reg_addr, const uint8_t *data, uint16_t len)
{
    (void)handle;
    (void)reg_addr;
    (void)data;
    (void)len;

    /* У реальному проєкті STM32 використовується HAL_I2C_Mem_Write():
     * return (HAL_I2C_Mem_Write((I2C_HandleTypeDef*)handle, ADXL345_I2C_ADDR_ALT_LOW, 
     *                           reg_addr, I2C_MEMADD_SIZE_8BIT, (uint8_t*)data, len, 100) == HAL_OK) ? 0 : -1;
     */
    return 0;
}

int main(void)
{
    printf("Ініціалізація C-драйвера ADXL345 для STM32...\n");

    adxl345_dev_t dev = {
        .read        = stm32_i2c_read,
        .write       = stm32_i2c_write,
        .user_handle = NULL, /* Вказати &hi2c1 у реальному коді */
        .i2c_addr    = ADXL345_I2C_ADDR_ALT_LOW
    };

    /* 1. Ініціалізація акселерометра */
    if (adxl345_init(&dev) != ADXL345_OK) {
        printf("Помилка: Не вдалося ініціалізувати ADXL345!\n");
        return -1;
    }

    /* 2. Конфігурація формату даних: +-4g, Full-Resolution mode */
    if (adxl345_set_data_format(&dev, ADXL345_RANGE_4G, true) != ADXL345_OK) {
        printf("Помилка налаштування DATA_FORMAT!\n");
        return -1;
    }

    /* 3. Налаштування ODR (частота вихідних даних = 200 Гц) */
    if (adxl345_set_bandwidth(&dev, ADXL345_ODR_200HZ) != ADXL345_OK) {
        printf("Помилка налаштування BW_RATE!\n");
        return -1;
    }

    /* 4. Налаштування апаратної лінії EXTI STM32 (Пін INT1 акселерометра) */
    stm32_exti_config_t exti_cfg = {
        .gpio_port   = NULL,
        .gpio_pin    = 0x0010U, /* GPIO_PIN_4 */
        .irq_channel = 10U      /* EXTI4_IRQn */
    };
    stm32_exti_init(&exti_cfg);

    /* 5. Налаштування FIFO-буфера в режим STREAM з порогом Watermark = 16 кадрів */
    const uint8_t watermark_threshold = 16U;
    if (adxl345_set_fifo_config(&dev, ADXL345_FIFO_STREAM, watermark_threshold) != ADXL345_OK) {
        printf("Помилка конфігурації FIFO_CTL!\n");
        return -1;
    }

    /* 6. Дозвіл переривання Watermark та його маршрутизація на вивід INT1 (0 = INT1) */
    if (adxl345_configure_interrupts(&dev, ADXL345_INT_WATERMARK, 0x00U) != ADXL345_OK) {
        printf("Помилка конфігурації INT_ENABLE / INT_MAP!\n");
        return -1;
    }

    printf("Драйвер успішно налаштовано. Очікування переривання Watermark...\n");

    /* Симуляція спрацьовування EXTI ISR від акселерометра */
    stm32_exti_gpio_isr_handler(exti_cfg.gpio_pin);

    /* Подійно-орієнтований головний цикл */
    if (stm32_exti_has_watermark_flag()) {
        stm32_exti_clear_watermark_flag();

        uint8_t int_src = 0;
        adxl345_read_interrupt_source(&dev, &int_src);

        if (int_src & ADXL345_INT_WATERMARK) {
            uint8_t entries = 0;
            adxl345_read_fifo_entries(&dev, &entries);
            printf("Отримано переривання Watermark! Кадрів у FIFO: %u\n", entries);

            for (uint8_t i = 0; i < entries; i++) {
                adxl345_raw_data_t raw;
                adxl345_accel_t accel;

                if (adxl345_read_raw_frame(&dev, &raw) == ADXL345_OK) {
                    adxl345_convert_raw_to_g(&dev, &raw, &accel);
                    printf("  Кадр [%02u]: Raw(X=%d, Y=%d, Z=%d) -> Accel(X=%.3fg, Y=%.3fg, Z=%.3fg)\n",
                           i + 1, raw.x, raw.y, raw.z, accel.x, accel.y, accel.z);
                }
            }
        }
    }

    return 0;
}
