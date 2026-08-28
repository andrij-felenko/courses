/* Контекст адаптера сенсора */
typedef struct {
    vendor_sensor_dev_t vendor_dev;
    sys_i2c_bus_t *bus;
    uint8_t i2c_addr;
    bool is_initialized;
} sensor_adapter_t;

/* Статичний місток читання для вендорського коду */
static int8_t adapter_c_read(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr) {
    if (!intf_ptr || !data || len == 0) {
        return VENDOR_E_NULL_PTR;
    }
    sensor_adapter_t *adapter = (sensor_adapter_t *)intf_ptr;
    bool ok = adapter->bus->read_reg(adapter->bus->bus_ctx, adapter->i2c_addr, reg_addr, data, len);
    return ok ? VENDOR_OK : VENDOR_E_COMM_FAIL;
}

/* Статичний місток запису для вендорського коду */
static int8_t adapter_c_write(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr) {
    if (!intf_ptr || !data || len == 0) {
        return VENDOR_E_NULL_PTR;
    }
    sensor_adapter_t *adapter = (sensor_adapter_t *)intf_ptr;
    bool ok = adapter->bus->write_reg(adapter->bus->bus_ctx, adapter->i2c_addr, reg_addr, data, len);
    return ok ? VENDOR_OK : VENDOR_E_COMM_FAIL;
}

/* Статичний місток затримки: гібридний виклик */
static void adapter_c_delay_us(uint32_t period_us, void *intf_ptr) {
    (void)intf_ptr;
    if (period_us >= 1000) {
        /* Для тривалих затримок — передача кванта RTOS (наприклад, vTaskDelay) */
        uint32_t ms = (period_us + 999) / 1000;
        /* Симуляція виклику RTOS-сну: rtos_sleep_ms(ms) */
        (void)ms;
    } else {
        /* Для коротких затримок — апаратний таймер / цикл DWT */
    }
}

/* Ініціалізація адаптера */
bool sensor_adapter_init(sensor_adapter_t *adapter, sys_i2c_bus_t *bus, uint8_t i2c_addr) {
    if (!adapter || !bus) {
        return false;
    }
    adapter->bus = bus;
    adapter->i2c_addr = i2c_addr;
    adapter->is_initialized = false;

    /* Налаштування полів вендорського дескриптора */
    adapter->vendor_dev.intf_ptr = adapter;
    adapter->vendor_dev.read = adapter_c_read;
    adapter->vendor_dev.write = adapter_c_write;
    adapter->vendor_dev.delay_us = adapter_c_delay_us;

    /* Ініціалізація вендорського чипа: перевірка Chip ID */
    uint8_t chip_id = 0;
    if (adapter->vendor_dev.read(0xD0, &chip_id, 1, adapter) != VENDOR_OK) {
        return false;
    }
    if (chip_id != 0x58 && chip_id != 0x60) {
        return false;
    }
    adapter->vendor_dev.chip_id = chip_id;
    adapter->is_initialized = true;
    return true;
}
