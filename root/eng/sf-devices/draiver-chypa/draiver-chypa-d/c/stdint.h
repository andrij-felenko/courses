#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    BUS_STATUS_OK = 0,
    BUS_STATUS_ERROR_TIMEOUT,
    BUS_STATUS_ERROR_NACK,
    BUS_STATUS_ERROR_BUS_LOCKED
} bus_status_t;

/* Інтерфейс апаратного зв'язку з шиною */
typedef struct {
    uint8_t dev_addr;
    bus_status_t (*read)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len);
    bus_status_t (*write)(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, uint16_t len);
    bus_status_t (*read_dma)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len);
    void         (*delay_ms)(uint32_t ms);
    void         (*bus_recover)(void);
} bus_interface_t;
