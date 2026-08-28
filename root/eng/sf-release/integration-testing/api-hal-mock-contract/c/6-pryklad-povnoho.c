#include "hal_interfaces_contract.h"
#include <assert.h>
#include <stdio.h>

/* Тестований драйвер барометра */
bool bmp280_read_temperature(hal_i2c_driver_t *i2c, uint16_t addr, int32_t *out_temp) {
    uint8_t raw_data[3] = {0};
    hal_status_t status = i2c->mem_read(i2c->ctx, addr, 0xFA, 1, raw_data, 3, 100);
    if (status != HAL_STATUS_OK) {
        return false;
    }
    *out_temp = ((int32_t)raw_data[0] << 12) | ((int32_t)raw_data[1] << 4) | (raw_data[2] >> 4);
    return true;
}

void test_bmp280_read_success_and_fault_injection(void) {
    mock_i2c_context_t mock_ctx;
    hal_i2c_driver_t i2c_driver;
    mock_i2c_init(&mock_ctx, 0x76, &i2c_driver);

    /* Заповнюємо регістри 0xFA, 0xFB, 0xFC значеннями температури */
    mock_ctx.registers[0xFA] = 0x80;
    mock_ctx.registers[0xFB] = 0x00;
    mock_ctx.registers[0xFC] = 0x00;

    int32_t temperature = 0;
    bool ok = bmp280_read_temperature(&i2c_driver, 0x76, &temperature);
    assert(ok == true);
    assert(temperature == (0x80 << 12));

    /* Інжектуємо апаратний збій таймауту */
    mock_ctx.injected_status = HAL_STATUS_ERR_TIMEOUT;
    ok = bmp280_read_temperature(&i2c_driver, 0x76, &temperature);
    assert(ok == false);
}
