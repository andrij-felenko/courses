/* i3c_controller.h - Базовий C-інтерфейс та структури контролера I3C */
#ifndef I3C_CONTROLLER_H
#define I3C_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define I3C_BROADCAST_ADDR  0x7E
#define I3C_CCC_ENTDAA      0x07
#define I3C_CCC_ENEC        0x00
#define I3C_CCC_DISEC       0x01
#define I3C_MAX_DEVICES     16

typedef enum {
    I3C_STATUS_OK = 0,
    I3C_STATUS_NACK,
    I3C_STATUS_BUS_LOST,
    I3C_STATUS_PARITY_ERROR,
    I3C_STATUS_TIMEOUT,
    I3C_STATUS_NO_DEVICES
} i3c_status_t;

typedef struct {
    uint64_t provisional_id; /* 48-бітний апаратний ID */
    uint8_t  bcr;            /* Bus Characteristics Register */
    uint8_t  dcr;            /* Device Characteristics Register */
    uint8_t  dynamic_addr;   /* Призначена 7-бітна динамічна адреса */
    bool     ibi_enabled;    /* Дозвіл переривань IBI */
} i3c_target_desc_t;

typedef struct {
    i3c_target_desc_t targets[I3C_MAX_DEVICES];
    size_t target_count;
    uint8_t next_free_addr;
} i3c_bus_context_t;

/* Обчислення непарного T-біта парності (Odd Parity) */
static inline uint8_t i3c_calc_t_bit(uint8_t byte) {
    byte ^= byte >> 4;
    byte ^= byte >> 2;
    byte ^= byte >> 1;
    return (uint8_t)(~byte & 0x01);
}

/* Ініціалізація контексту шини */
void i3c_bus_init(i3c_bus_context_t *ctx);

/* Процедура динамічного призначення адрес (ENTDAA) */
i3c_status_t i3c_perform_daa(i3c_bus_context_t *ctx);

/* Запис блоку даних цільовому пристрою у режимі SDR */
i3c_status_t i3c_sdr_write(i3c_bus_context_t *ctx, uint8_t dyn_addr,
                           const uint8_t *data, size_t len);

/* Зчитування блоку даних від цільового пристрою у режимі SDR */
i3c_status_t i3c_sdr_read(i3c_bus_context_t *ctx, uint8_t dyn_addr,
                          uint8_t *buffer, size_t max_len, size_t *actual_len);

/* Обробник внутрішньосмугового переривання IBI */
i3c_status_t i3c_handle_ibi(i3c_bus_context_t *ctx, uint8_t *winning_addr,
                            uint8_t *mdb);

#endif /* I3C_CONTROLLER_H */
