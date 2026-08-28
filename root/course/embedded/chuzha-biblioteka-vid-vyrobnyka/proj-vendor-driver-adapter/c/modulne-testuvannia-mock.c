#include <string.h>
#include <assert.h>

/* Структура програмного мока шини */
typedef struct {
    uint8_t registers[256];
    bool inject_nack;
    uint32_t read_count;
    uint32_t write_count;
} mock_i2c_state_t;

static bool mock_read(void *ctx, uint8_t dev_addr, uint8_t reg, uint8_t *buf, size_t len) {
    (void)dev_addr;
    mock_i2c_state_t *mock = (mock_i2c_state_t *)ctx;
    if (mock->inject_nack) {
        return false; /* Імітація відсутності відповіді від чипа */
    }
    for (size_t i = 0; i < len; ++i) {
        buf[i] = mock->registers[(reg + i) & 0xFF];
    }
    mock->read_count++;
    return true;
}

static bool mock_write(void *ctx, uint8_t dev_addr, uint8_t reg, const uint8_t *buf, size_t len) {
    (void)dev_addr;
    mock_i2c_state_t *mock = (mock_i2c_state_t *)ctx;
    if (mock->inject_nack) {
        return false;
    }
    for (size_t i = 0; i < len; ++i) {
        mock->registers[(reg + i) & 0xFF] = buf[i];
    }
    mock->write_count++;
    return true;
}

void run_c_adapter_tests(void) {
    mock_i2c_state_t mock_state;
    memset(&mock_state, 0, sizeof(mock_state));
    mock_state.registers[0xD0] = 0x60; /* Валідний Chip ID BME280 */

    sys_i2c_bus_t mock_bus = {
        .read_reg = mock_read,
        .write_reg = mock_write,
        .bus_ctx = &mock_state
    };

    sensor_adapter_t adapter;

    /* Тест 1: Успішна ініціалізація */
    bool ok = sensor_adapter_init(&adapter, &mock_bus, 0x76);
    assert(ok == true);
    assert(adapter.is_initialized == true);

    /* Тест 2: Fault Injection — шина вибиває помилку зв'язку */
    mock_state.inject_nack = true;
    sensor_adapter_t failed_adapter;
    ok = sensor_adapter_init(&failed_adapter, &mock_bus, 0x76);
    assert(ok == false);
    assert(failed_adapter.is_initialized == false);
}
