#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди помилок вендорського SDK */
#define VENDOR_OK           0
#define VENDOR_E_NULL_PTR  -1
#define VENDOR_E_COMM_FAIL -2
#define VENDOR_E_INVALID_ID -3

/* Типи колбеків вендорського Platform Abstraction Layer */
typedef int8_t (*vendor_read_fn)(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr);
typedef int8_t (*vendor_write_fn)(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr);
typedef void (*vendor_delay_us_fn)(uint32_t period_us, void *intf_ptr);

/* Структура дескриптора вендорського драйвера */
typedef struct {
    uint8_t chip_id;
    void *intf_ptr;
    vendor_read_fn read;
    vendor_write_fn write;
    vendor_delay_us_fn delay_us;
} vendor_sensor_dev_t;

/* Системний інтерфейс апаратної шини */
typedef struct {
    bool (*read_reg)(void *bus_ctx, uint8_t dev_addr, uint8_t reg, uint8_t *buf, size_t len);
    bool (*write_reg)(void *bus_ctx, uint8_t dev_addr, uint8_t reg, const uint8_t *buf, size_t len);
    void *bus_ctx;
} sys_i2c_bus_t;

/* Системна структура виміряних величин */
typedef struct {
    int32_t temperature_centi_deg; /* Температура в сотих частках градуса Цельсія */
    uint32_t pressure_pa;          /* Тиск у Паскалях */
} sensor_data_t;
