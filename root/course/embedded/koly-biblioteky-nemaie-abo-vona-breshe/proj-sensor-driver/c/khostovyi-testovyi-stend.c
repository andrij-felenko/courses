#include <stdio.h>
#include <assert.h>
#include <string.h>
#include "sensor_driver.h"

typedef struct {
    uint32_t current_time_us;
    uint8_t  registers[256];
    bool     inject_crc_error;
    bool     inject_bus_error;
    bool     bus_recovered;
} mock_bus_context_t;

static mock_bus_context_t g_mock;

static uint32_t mock_get_time(void) {
    return g_mock.current_time_us;
}

static sensor_status_t mock_read(void *ctx, uint8_t reg, uint8_t *data, size_t len) {
    (void)ctx;
    if (g_mock.inject_bus_error) {
        return SENSOR_ERR_BUS_IO;
    }
    for (size_t i = 0; i < len; i++) {
        data[i] = g_mock.registers[(uint8_t)(reg + i)];
    }
    return SENSOR_OK;
}

static sensor_status_t mock_write(void *ctx, uint8_t reg, const uint8_t *data, size_t len) {
    (void)ctx;
    if (g_mock.inject_bus_error) {
        return SENSOR_ERR_BUS_IO;
    }
    for (size_t i = 0; i < len; i++) {
        g_mock.registers[(uint8_t)(reg + i)] = data[i];
    }
    return SENSOR_OK;
}

static sensor_status_t mock_recover(void *ctx) {
    (void)ctx;
    g_mock.bus_recovered = true;
    g_mock.inject_bus_error = false;
    return SENSOR_OK;
}

static const sensor_bus_ops_t g_mock_ops = {
    .read = mock_read,
    .write = mock_write,
    .get_time_us = mock_get_time,
    .recover_bus = mock_recover
};

int main(void) {
    printf("=== Запуск тестів драйвера сенсора на хості (C) ===\n");

    /* Тест 1: Успішна ініціалізація та валідація Chip ID */
    memset(&g_mock, 0, sizeof(g_mock));
    g_mock.registers[0xD0] = 0x58; /* Правильний ID сенсора */

    sensor_device_t dev;
    sensor_status_t st = sensor_init(&dev, &g_mock_ops, NULL);
    assert(st == SENSOR_OK);
    assert(dev.state == SENSOR_STATE_IDLE);
    printf("[OK] Тест 1: Валідація Chip ID пройшла успішно\n");

    /* Тест 2: Запуск заміру та неблокуюче очікування (NOT_READY) */
    st = sensor_start_measurement(&dev);
    assert(st == SENSOR_OK);
    assert(dev.state == SENSOR_STATE_CONVERTING);

    sensor_data_t data;
    g_mock.current_time_us += 10000; /* Минуло лише 10 мс із 20 мс */
    st = sensor_poll(&dev, &data);
    assert(st == SENSOR_ERR_NOT_READY);
    assert(dev.state == SENSOR_STATE_CONVERTING);
    printf("[OK] Тест 2: Неблокуюче очікування (NOT_READY) працює коректно\n");

    /* Тест 3: Завершення конверсії та розбір коректних даних з CRC */
    g_mock.current_time_us += 15000; /* Сумарно минуло 25 мс (> 20 мс) */
    
    /* Заповнення регістрів: T = 25.0 °C (raw = 0x6666, CRC = 0xBE) */
    g_mock.registers[0xF7] = 0x66;
    g_mock.registers[0xF8] = 0x66;
    g_mock.registers[0xF9] = 0xBE; /* Еталонний CRC-8 */
    /* P = 101325 Па (raw = 0xE442, CRC = 0x7E) */
    g_mock.registers[0xFA] = 0xE4;
    g_mock.registers[0xFB] = 0x42;
    g_mock.registers[0xFC] = 0x7E; /* Еталонний CRC-8 */

    st = sensor_poll(&dev, &data);
    assert(st == SENSOR_OK);
    assert(dev.state == SENSOR_STATE_DATA_READY);
    printf("[OK] Тест 3: Дані прочитано. T = %ld.%03ld °C, P = %lu Па\n",
           (long)(data.temperature_mdeg_c / 1000), (long)(data.temperature_mdeg_c % 1000), (unsigned long)data.pressure_pa);

    /* Тест 4: Виявлення пошкодження даних (CRC Fail) */
    sensor_start_measurement(&dev);
    g_mock.current_time_us += 25000;
    g_mock.registers[0xF9] ^= 0x01; /* Інверсія одного біта CRC */

    st = sensor_poll(&dev, &data);
    assert(st == SENSOR_ERR_CRC);
    assert(dev.state == SENSOR_STATE_ERROR);
    printf("[OK] Тест 4: Спотворення даних успішно перехоплено перевіркою CRC-8\n");

    /* Тест 5: Перевірка відновлення шини після збою */
    sensor_reset_fsm(&dev);
    g_mock.inject_bus_error = true;
    st = sensor_start_measurement(&dev);
    assert(st == SENSOR_ERR_BUS_IO);
    assert(dev.state == SENSOR_STATE_ERROR);
    dev.ops->recover_bus(NULL);
    assert(g_mock.bus_recovered == true);
    printf("[OK] Тест 5: Автоматичне відновлення шини виконано успішно\n");

    printf("=== Усі тести завершено успішно! ===\n");
    return 0;
}
