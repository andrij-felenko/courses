/* Узагальнений інтерфейс зв'язку з шиною */
typedef struct bus_interface_s {
    void* user_ctx; /* Покажчик на дескриптор шини (наприклад, i2c_handle_t*) */
    driver_status_t (*write_reg)(void* ctx, uint8_t dev_addr, uint8_t reg_addr,
                                 const uint8_t* data, size_t len);
    driver_status_t (*read_reg)(void* ctx, uint8_t dev_addr, uint8_t reg_addr,
                                uint8_t* data, size_t len);
} bus_interface_t;

/* Драйвер датчика знає лише про шинний інтерфейс */
typedef struct {
    bus_interface_t bus;
    uint8_t dev_addr;
    int32_t last_temperature;
} sensor_driver_t;

driver_status_t sensor_init(sensor_driver_t* sensor, bus_interface_t bus, uint8_t dev_addr) {
    if (sensor == NULL || bus.read_reg == NULL || bus.write_reg == NULL) {
        return DRIVER_STATUS_INVALID_PARAM;
    }
    sensor->bus = bus;
    sensor->dev_addr = dev_addr;

    /* Читання Chip ID через абстрактну шину */
    uint8_t chip_id = 0;
    driver_status_t st = sensor->bus.read_reg(sensor->bus.user_ctx, sensor->dev_addr, 0xD0, &chip_id, 1);
    if (st != DRIVER_STATUS_OK || chip_id != 0x58) {
        return DRIVER_STATUS_BUS_ERROR;
    }
    return DRIVER_STATUS_OK;
}
