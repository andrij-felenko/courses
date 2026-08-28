// targets/host_test_main.c
#include <stdio.h>
#include <assert.h>
#include "hal/hal_i2c.h"
#include "bsp/bsp_bme280.h"
#include "services/event_queue.h"
#include "app/app_telemetry.h"

// Емулятор масиву регістрів I2C на робочому комп'ютері
typedef struct {
    uint8_t registers[256];
} host_mock_i2c_ctx_t;

static hal_i2c_status_t mock_read(void* ctx, uint8_t dev_addr, uint8_t reg, uint8_t* data, size_t len) {
    (void)dev_addr;
    host_mock_i2c_ctx_t* m = (host_mock_i2c_ctx_t*)ctx;
    for (size_t i = 0; i < len; ++i) {
        data[i] = m->registers[(reg + i) & 0xFF];
    }
    return HAL_I2C_OK;
}

int main(void) {
    host_mock_i2c_ctx_t mock_ctx = {0};
    mock_ctx.registers[0xD0] = 0x60; // Chip ID давача BME280
    // Імітація температури 40.0 °C (вище порога 35.0 °C)
    mock_ctx.registers[0xF7 + 3] = 0x8A;
    mock_ctx.registers[0xF7 + 4] = 0x6E;
    mock_ctx.registers[0xF7 + 5] = 0x70;

    hal_i2c_bus_ops_t mock_ops = {.read_reg = mock_read, .write_reg = NULL};
    hal_i2c_bus_t bus = {.ops = &mock_ops, .context = &mock_ctx};

    bsp_bme280_storage_t storage;
    bsp_bme280_t* sensor = bsp_bme280_init(&storage, &bus, 0x76);
    assert(sensor != NULL);

    event_queue_t queue;
    event_queue_init(&queue);

    app_telemetry_t app;
    app_telemetry_init(&app, sensor, &queue, 35.0f);

    // Імітуємо надходження періодичного сигналу опитування від таймера
    event_t trigger = {.type = EVT_SENSOR_TRIGGER, .timestamp_ms = 1000};
    app_telemetry_process_event(&app, &trigger);

    // Перевіряємо реакцію бізнес-логіки: подія тривоги має з'явитися в черзі
    event_t alert_evt;
    bool pop_ok = event_queue_pop(&queue, &alert_evt);
    assert(pop_ok == true);
    assert(alert_evt.type == EVT_ALERT_THRESHOLD);

    printf("Unit test PASSED: Business logic executed cleanly on Host PC without MCU hardware!\n");
    return 0;
}
