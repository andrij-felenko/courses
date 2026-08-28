#include <stdio.h>
#include <assert.h>

int main(void) {
    printf("[C99 Mock Test] Початок тестування драйвера BME280...\n");

    /* Створення контексту та ініціалізація пам'яті Mock I2C */
    mock_i2c_ctx_t i2c_ctx;
    memset(&i2c_ctx, 0, sizeof(i2c_ctx));
    i2c_ctx.expected_addr = BME280_I2C_ADDR_PRIM;

    /* Запис очікуваного Chip ID */
    i2c_ctx.registers[BME280_REG_CHIP_ID] = BME280_CHIP_ID_VAL;

    /* Запис тестових калібрувальних коефіцієнтів: dig_T1=27504, dig_T2=26435, dig_T3=-1000 */
    i2c_ctx.registers[BME280_REG_CALIB00 + 0] = 0x70;
    i2c_ctx.registers[BME280_REG_CALIB00 + 1] = 0x6B;
    i2c_ctx.registers[BME280_REG_CALIB00 + 2] = 0x43;
    i2c_ctx.registers[BME280_REG_CALIB00 + 3] = 0x67;
    i2c_ctx.registers[BME280_REG_CALIB00 + 4] = 0x18;
    i2c_ctx.registers[BME280_REG_CALIB00 + 5] = 0xFC;

    /* Запис сирих даних температури: adc_T = 519888 */
    i2c_ctx.registers[BME280_REG_TEMP_MSB + 0] = 0x7E;
    i2c_ctx.registers[BME280_REG_TEMP_MSB + 1] = 0xEC;
    i2c_ctx.registers[BME280_REG_TEMP_MSB + 2] = 0x00;

    /* Збирання екземпляра HAL */
    hal_i2c_bus_t mock_bus = {
        .ops = &mock_i2c_ops,
        .ctx = &i2c_ctx
    };

    /* Ініціалізація драйвера датчика */
    bme280_driver_t sensor;
    hal_status_t status = bme280_init(&sensor, &mock_bus, BME280_I2C_ADDR_PRIM);
    assert(status == HAL_STATUS_OK);
    printf(" -> Ініціалізація датчика успішна, Chip ID валідний (0x%02X)\n", BME280_CHIP_ID_VAL);

    /* Зчитування та перевірка обчисленої температури */
    int32_t temp_c_x100 = 0;
    status = bme280_read_temperature(&sensor, &temp_c_x100);
    assert(status == HAL_STATUS_OK);
    printf(" -> Температура: %d.%02d °C (очікувалось ~25.08 °C)\n", temp_c_x100 / 100, temp_c_x100 % 100);
    assert(temp_c_x100 >= 2400 && temp_c_x100 <= 2600);

    /* Перевірка обробки помилки NACK */
    i2c_ctx.force_nack = true;
    status = bme280_read_temperature(&sensor, &temp_c_x100);
    assert(status == HAL_STATUS_NACK);
    printf(" -> Тест реакції на відсутність відповіді (NACK) пройдено успішно.\n");

    printf("[C99 Mock Test] Усі перевірки завершено успішно!\n");
    return 0;
}
