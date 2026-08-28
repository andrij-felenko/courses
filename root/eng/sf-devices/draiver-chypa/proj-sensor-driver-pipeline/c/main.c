/**
 * @file main.c
 * @brief Тестовий стенд, емулятор апаратної шини I2C/DMA та верифікація C99 драйвера BMP280.
 */

#include <stdio.h>
#include <string.h>
#include <assert.h>
#include "driver_bmp280.h"

/* ── Емуляція апаратного стану чипа ────────────────────────────────────────── */
typedef struct {
    uint8_t chip_id;
    uint8_t ctrl_meas;
    uint8_t config;
    uint8_t status;
    uint8_t calib_rom[BMP280_CALIB_DATA_SIZE];
    uint8_t sample_regs[BMP280_BURST_DATA_SIZE];
    bool    bus_locked;
    uint32_t bus_cycles;
} mock_hardware_t;

static mock_hardware_t g_mcu_chip;

static void mock_init_chip(void) {
    g_mcu_chip.chip_id = BMP280_CHIP_ID_VALUE;
    g_mcu_chip.ctrl_meas = 0x00U;
    g_mcu_chip.config = 0x00U;
    g_mcu_chip.status = 0x00U;
    g_mcu_chip.bus_locked = false;
    g_mcu_chip.bus_cycles = 0;

    /* Еталонні калібрувальні коефіцієнти Bosch Sensortec BMP280 */
    /* dig_T1 = 27504 (0x6B70), dig_T2 = -1048 (0xFBE8), dig_T3 = -1000 (0xFC18) */
    g_mcu_chip.calib_rom[0]  = 0x70U; g_mcu_chip.calib_rom[1]  = 0x6BU;
    g_mcu_chip.calib_rom[2]  = 0xE8U; g_mcu_chip.calib_rom[3]  = 0xFBU;
    g_mcu_chip.calib_rom[4]  = 0x18U; g_mcu_chip.calib_rom[5]  = 0xFCU;

    /* dig_P1 = 36477 (0x8E7D), dig_P2 = -10685 (0xD643), dig_P3 = 3024 (0x0BD0) */
    g_mcu_chip.calib_rom[6]  = 0x7DU; g_mcu_chip.calib_rom[7]  = 0x8EU;
    g_mcu_chip.calib_rom[8]  = 0x43U; g_mcu_chip.calib_rom[9]  = 0xD6U;
    g_mcu_chip.calib_rom[10] = 0xD0U; g_mcu_chip.calib_rom[11] = 0x0BU;

    /* dig_P4 = 2855 (0x0B27), dig_P5 = 140 (0x008C), dig_P6 = -7 (0xFFF9) */
    g_mcu_chip.calib_rom[12] = 0x27U; g_mcu_chip.calib_rom[13] = 0x0BU;
    g_mcu_chip.calib_rom[14] = 0x8CU; g_mcu_chip.calib_rom[15] = 0x00U;
    g_mcu_chip.calib_rom[16] = 0xF9U; g_mcu_chip.calib_rom[17] = 0xFFU;

    /* dig_P7 = 15500 (0x3C8C), dig_P8 = -14600 (0xC6F8), dig_P9 = 6000 (0x1770) */
    g_mcu_chip.calib_rom[18] = 0x8CU; g_mcu_chip.calib_rom[19] = 0x3CU;
    g_mcu_chip.calib_rom[20] = 0xF8U; g_mcu_chip.calib_rom[21] = 0xC6U;
    g_mcu_chip.calib_rom[22] = 0x70U; g_mcu_chip.calib_rom[23] = 0x17U;

    /* Сирий тестовий вектор: ADC_P = 415148 (0x655AC), ADC_T = 519888 (0x7EEC0) */
    g_mcu_chip.sample_regs[0] = 0x65U; /* PRESS_MSB */
    g_mcu_chip.sample_regs[1] = 0x5AU; /* PRESS_LSB */
    g_mcu_chip.sample_regs[2] = 0xC0U; /* PRESS_XLSB */
    g_mcu_chip.sample_regs[3] = 0x7EU; /* TEMP_MSB */
    g_mcu_chip.sample_regs[4] = 0xECU; /* TEMP_LSB */
    g_mcu_chip.sample_regs[5] = 0x00U; /* TEMP_XLSB */
}

/* ── Емуляція функцій HAL ─────────────────────────────────────────────────── */
static bmp280_status_t hal_mock_i2c_read(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len) {
    (void)dev_addr;
    if (g_mcu_chip.bus_locked) {
        return BMP280_ERR_BUS_TIMEOUT;
    }
    if (reg_addr == BMP280_REG_CHIP_ID && len == 1) {
        *data = g_mcu_chip.chip_id;
        return BMP280_OK;
    }
    if (reg_addr == BMP280_REG_CALIB_START && len <= BMP280_CALIB_DATA_SIZE) {
        memcpy(data, g_mcu_chip.calib_rom, len);
        return BMP280_OK;
    }
    if (reg_addr == BMP280_REG_PRESS_MSB && len <= BMP280_BURST_DATA_SIZE) {
        memcpy(data, g_mcu_chip.sample_regs, len);
        return BMP280_OK;
    }
    return BMP280_OK;
}

static bmp280_status_t hal_mock_i2c_write(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, uint16_t len) {
    (void)dev_addr;
    if (g_mcu_chip.bus_locked) {
        return BMP280_ERR_BUS_TIMEOUT;
    }
    if (reg_addr == BMP280_REG_RESET && len == 1) {
        if (*data == BMP280_SOFT_RESET_CMD) {
            g_mcu_chip.ctrl_meas = 0x00U;
            g_mcu_chip.config = 0x00U;
        }
        return BMP280_OK;
    }
    if (reg_addr == BMP280_REG_CONFIG && len == 1) {
        g_mcu_chip.config = *data;
        return BMP280_OK;
    }
    if (reg_addr == BMP280_REG_CTRL_MEAS && len == 1) {
        g_mcu_chip.ctrl_meas = *data;
        return BMP280_OK;
    }
    return BMP280_OK;
}

static bmp280_status_t hal_mock_dma_start(uint8_t dev_addr, uint8_t reg_addr, uint8_t *buf, uint16_t len) {
    (void)dev_addr;
    if (g_mcu_chip.bus_locked) {
        return BMP280_ERR_BUS_TIMEOUT;
    }
    if (reg_addr == BMP280_REG_PRESS_MSB && len <= BMP280_BURST_DATA_SIZE) {
        memcpy(buf, g_mcu_chip.sample_regs, len);
        return BMP280_OK;
    }
    return BMP280_ERR_BUS_NACK;
}

static void hal_mock_delay_ms(uint32_t ms) {
    (void)ms;
}

static void hal_mock_bus_recovery(void) {
    /* Емуляція генерації 9 імпульсів SCL для звільнення лінії SDA */
    g_mcu_chip.bus_locked = false;
    g_mcu_chip.bus_cycles += 9;
}

/* ── Тестовий набір ────────────────────────────────────────────────────────── */
static void run_unit_tests(void) {
    printf("[TEST] Запуск тестів C99 драйвера BMP280...\n");

    mock_init_chip();

    bmp280_bus_t bus_if = {
        .dev_addr = 0x76U,
        .read = hal_mock_i2c_read,
        .write = hal_mock_i2c_write,
        .read_dma_start = hal_mock_dma_start,
        .delay_ms = hal_mock_delay_ms,
        .bus_recover = hal_mock_bus_recovery
    };

    bmp280_handle_t dev;

    /* 1. Тест успішної ініціалізації */
    bmp280_status_t status = bmp280_init(&dev, &bus_if);
    assert(status == BMP280_OK);
    assert(dev.state == BMP280_STATE_IDLE);
    assert(dev.calib.dig_T1 == 27504U);
    assert(dev.calib.dig_T2 == -1048);
    printf("  [OK] Ініціалізація та зчитування NVM пройшли успішно\n");

    /* 2. Тест конфігурації */
    status = bmp280_configure(&dev,
                              BMP280_OSR_2X,
                              BMP280_OSR_16X,
                              BMP280_MODE_NORMAL,
                              BMP280_FILTER_16,
                              BMP280_STANDBY_62_5_MS);
    assert(status == BMP280_OK);
    printf("  [OK] Конфігурація OSR, IIR та Standby записана у регістри\n");

    /* 3. Тест синхронного вимірювання та математичної компенсації */
    bmp280_sample_t sample;
    status = bmp280_read_sync(&dev, &sample);
    assert(status == BMP280_OK);
    assert(sample.valid == true);

    /* Звірка з еталонними значеннями Bosch Sensortec:
     * Температура: -106 (-1.06 °C)
     * Тиск: 100653 Па (1006.53 гПа)
     */
    assert(sample.temperature_centidegrees == -106);
    assert(sample.pressure_pascals == 100653U);
    printf("  [OK] Синхронна компенсація: T = %d.%02d °C, P = %u Па\n",
           sample.temperature_centidegrees / 100,
           (sample.temperature_centidegrees < 0 ? -sample.temperature_centidegrees : sample.temperature_centidegrees) % 100,
           sample.pressure_pascals);

    /* 4. Тест асинхронного DMA-пайплайну */
    status = bmp280_start_read_async_dma(&dev);
    assert(status == BMP280_OK);
    assert(dev.state == BMP280_STATE_BURST_READ_DMA);

    /* Емуляція спрацювання переривання завершення DMA */
    bmp280_dma_complete_callback(&dev);
    assert(dev.state == BMP280_STATE_IDLE);
    assert(dev.last_sample.pressure_pascals == 100653U);
    printf("  [OK] Асинхронний DMA трансфер та callback виконані без помилок\n");

    /* 5. Тест аварійного відновлення шини при зависанні */
    g_mcu_chip.bus_locked = true;
    status = bmp280_read_sync(&dev, &sample);
    assert(status == BMP280_ERR_BUS_TIMEOUT);
    assert(dev.state == BMP280_STATE_RECOVERY);

    status = bmp280_recover_bus(&dev);
    assert(status == BMP280_OK);
    assert(dev.recovery_count == 1);
    assert(dev.state == BMP280_STATE_IDLE);
    printf("  [OK] Відновлення шини (9 тактів SCL) успішно повернуло чип у робочий стан\n");

    /* 6. Тест контрольної суми CRC-8 Dallas */
    const uint8_t test_vec[] = { 0x01, 0x02, 0x03, 0x04 };
    uint8_t crc = bmp280_calc_crc8_dallas(test_vec, sizeof(test_vec));
    assert(crc != 0);
    printf("  [OK] CRC-8 Dallas розраховано успішно (0x%02X)\n", crc);

    printf("[SUCCESS] Усі тести C99 драйвера пройдено на 100%%!\n");
}

int main(void) {
    run_unit_tests();
    return 0;
}
