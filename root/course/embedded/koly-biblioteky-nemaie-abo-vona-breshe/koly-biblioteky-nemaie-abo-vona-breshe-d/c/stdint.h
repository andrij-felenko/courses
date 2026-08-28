#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    BUS_OK          =  0,
    BUS_ERR_TIMEOUT = -1,
    BUS_ERR_NACK    = -2,
    BUS_ERR_IO      = -3
} bus_status_t;

/* Інтерфейс функціональних покажчиків для шини */
typedef struct {
    /* Читання масиву байтів із вказаного субрегістра */
    bus_status_t (*read_reg)(void *user_ctx, uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, size_t len);
    /* Запис масиву байтів у вказаний субрегістр */
    bus_status_t (*write_reg)(void *user_ctx, uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, size_t len);
    /* Отримання поточного монотонного часу в мікросекундах */
    uint32_t (*get_time_us)(void);
} bus_interface_t;
