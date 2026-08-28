/**
 * @file bus_transaction_c99.h
 * @brief Уніфікований інтерфейс рівня транзакцій на C99.
 */

#ifndef BUS_TRANSACTION_C99_H_
#define BUS_TRANSACTION_C99_H_

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    BUS_STATUS_OK              =  0,
    BUS_STATUS_ERR_PARAM       = -1,
    BUS_STATUS_ERR_TIMEOUT     = -2,
    BUS_STATUS_ERR_NACK        = -3,
    BUS_STATUS_ERR_ARBITRATION = -4,
    BUS_STATUS_ERR_IO          = -5
} bus_status_t;

typedef struct bus_interface bus_interface_t;

/**
 * @brief Таблиця функціональних покажчиків (VTable).
 */
typedef struct {
    bus_status_t (*read_reg)(void *ctx, uint16_t reg, uint8_t *rx_buf, size_t len);
    bus_status_t (*write_reg)(void *ctx, uint16_t reg, const uint8_t *tx_buf, size_t len);
    bus_status_t (*lock)(void *ctx, uint32_t timeout_ms);
    bus_status_t (*unlock)(void *ctx);
} bus_ops_t;

/**
 * @brief Дескриптор екземпляра шини.
 */
struct bus_interface {
    const bus_ops_t *ops;  /**< Покажчик на незмінну таблицю операцій */
    void            *ctx;  /**< Покажчик на приватний контекст апаратного адаптера */
};

/* Зручні інлайн-обгортки */
static inline bus_status_t bus_read_reg(const bus_interface_t *bus, uint16_t reg, uint8_t *buf, size_t len) {
    if (!bus || !bus->ops || !bus->ops->read_reg) return BUS_STATUS_ERR_PARAM;
    return bus->ops->read_reg(bus->ctx, reg, buf, len);
}

static inline bus_status_t bus_write_reg(const bus_interface_t *bus, uint16_t reg, const uint8_t *buf, size_t len) {
    if (!bus || !bus->ops || !bus->ops->write_reg) return BUS_STATUS_ERR_PARAM;
    return bus->ops->write_reg(bus->ctx, reg, buf, len);
}

static inline bus_status_t bus_read_u8(const bus_interface_t *bus, uint16_t reg, uint8_t *val) {
    return bus_read_reg(bus, reg, val, 1);
}

static inline bus_status_t bus_write_u8(const bus_interface_t *bus, uint16_t reg, uint8_t val) {
    return bus_write_reg(bus, reg, &val, 1);
}

/**
 * @brief Атомарна операція читання-модифікації-запису (Read-Modify-Write).
 */
bus_status_t bus_modify_reg(const bus_interface_t *bus, uint16_t reg, uint8_t clear_mask, uint8_t set_mask);

#endif /* BUS_TRANSACTION_C99_H_ */
