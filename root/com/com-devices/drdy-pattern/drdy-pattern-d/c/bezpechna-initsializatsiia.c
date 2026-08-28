#include <stdint.h>
#include <stdbool.h>

#define IMU_SPI_PORT         0
#define IMU_REG_WHO_AM_I     0x0F
#define IMU_EXPECTED_CHIP_ID 0x6C
#define IMU_REG_CTRL1_XL     0x10
#define IMU_REG_STATUS       0x1E
#define IMU_REG_OUTX_L_A     0x28

/* Прототипи системних функцій шинного обміну */
bool spi_transfer_byte(uint8_t reg, uint8_t *val);
bool spi_burst_read(uint8_t start_reg, uint8_t *buf, uint16_t len);
bool spi_write_byte(uint8_t reg, uint8_t val);
void exti_enable_line(uint8_t pin_index);

bool sensor_safe_init(void)
{
    uint8_t chip_id = 0;
    uint8_t dummy_buf[14];

    /* Крок 1. Перевірка ідентифікатора кристала */
    if (!spi_transfer_byte(IMU_REG_WHO_AM_I, &chip_id) || chip_id != IMU_EXPECTED_CHIP_ID) {
        return false; /* Помилка апаратної шини або невірний тип мікросхеми */
    }

    /* Крок 2. КРИТИЧНИЙ ЕТАП: Холосте вичитування (Dummy Flush)
     * Скидаємо можливий завислий активний рівень Latch після перезавантаження MCU */
    (void)spi_burst_read(IMU_REG_STATUS, dummy_buf, sizeof(dummy_buf));

    /* Крок 3. Налаштування ODR = 1000 Гц, конфігурація виводу DRDY (Active-Low, Latched) */
    if (!spi_write_byte(IMU_REG_CTRL1_XL, 0x80)) { /* 0x80 = 1000 Hz High-Performance */
        return false;
    }

    /* Крок 4. Додаткове читання статусу для гарантії повернення лінії nINT у високий рівень */
    uint8_t status_verify = 0;
    spi_transfer_byte(IMU_REG_STATUS, &status_verify);

    /* Крок 5. Тільки тепер вмикаємо переривання EXTI в контролері MCU */
    exti_enable_line(4);

    return true;
}
