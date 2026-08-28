/**
 * @file bus_transaction.h
 * @brief Уніфікований інтерфейс рівня транзакцій (Transaction Layer) на C99.
 */

#ifndef BUS_TRANSACTION_H_
#define BUS_TRANSACTION_H_

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Уніфіковані коди результату виконання транзакції.
 */
typedef enum {
    BUS_OK                =  0,  /**< Транзакція успішно завершена */
    BUS_ERR_INVALID_ARG   = -1,  /**< Некоректні вхідні параметри (NULL-покажчик, нульова довжина) */
    BUS_ERR_TIMEOUT       = -2,  /**< Таймаут очікування апаратного завершення обміну */
    BUS_ERR_NACK          = -3,  /**< Відсутність підтвердження адреси чи даних на шині I2C */
    BUS_ERR_ARBITRATION   = -4,  /**< Втрата арбітражу на мультимайстер-шині I2C */
    BUS_ERR_BUSY          = -5,  /**< Шина зайнята іншою транзакцією або заблокована */
    BUS_ERR_DMA           = -6,  /**< Апаратна помилка каналу прямого доступу до пам'яті */
    BUS_ERR_IO            = -7   /**< Фізична помилка ліній зв'язку або апаратного периферійного блоку */
} bus_status_t;

/**
 * @brief Прапорці кадрування протоколу та модифікації адресного байта.
 */
typedef enum {
    BUS_FLAG_NONE          = 0x00, /**< Стандартне кадрування без модифікації адреси */
    BUS_FLAG_SPI_READ_MSB  = 0x01, /**< SPI: Встановити біт 7 у '1' для операції читання (Bosch/InvenSense) */
    BUS_FLAG_SPI_READ_LSB  = 0x02, /**< SPI: Встановити біт 0 у '1' для читання (Analog Devices) */
    BUS_FLAG_AUTO_INC      = 0x04, /**< SPI: Встановити біт 6 у '1' для автоінкременту регістрів (STMicro) */
    BUS_FLAG_REG_16BIT     = 0x08, /**< 16-бітна адреса регістрів замість стандартної 8-бітної */
    BUS_FLAG_USE_DUMMY     = 0x10  /**< Необхідність передачі 1 dummy-байта перед даними при швидкісному SPI */
} bus_flags_t;

/* Попереднє оголошення інтерфейсу шини */
typedef struct bus_interface bus_interface_t;

/**
 * @brief Віртуальна таблиця операцій шини (Bus VTable).
 */
typedef struct {
    /**
     * @brief Зчитування послідовності байтів із вказаного регістра.
     */
    bus_status_t (*read_reg)(void *ctx, uint16_t reg_addr, uint8_t *data, size_t len);

    /**
     * @brief Запис послідовності байтів у вказаний регістр.
     */
    bus_status_t (*write_reg)(void *ctx, uint16_t reg_addr, const uint8_t *data, size_t len);

    /**
     * @brief Прямий повнодуплексний або напівдуплексний блоковий трансфер.
     */
    bus_status_t (*transfer)(void *ctx, const uint8_t *tx_data, uint8_t *rx_data, size_t len);

    /**
     * @brief Захоплення м'ютекса для блокування шини в RTOS.
     */
    bus_status_t (*lock)(void *ctx, uint32_t timeout_ms);

    /**
     * @brief Звільнення м'ютекса шини.
     */
    bus_status_t (*unlock)(void *ctx);
} bus_ops_t;

/**
 * @brief Загальний дескриптор шини.
 */
struct bus_interface {
    const bus_ops_t *ops;   /**< Таблиця функціональних покажчиків */
    void            *ctx;   /**< Приватний контекст апаратного адаптера */
    uint32_t         flags; /**< Набір прапорців bus_flags_t */
};

/* Допоміжні інлайн-обгортки для компактності коду драйвера */
static inline bus_status_t bus_read_reg(const bus_interface_t *bus, uint16_t reg, uint8_t *data, size_t len) {
    if (!bus || !bus->ops || !bus->ops->read_reg) return BUS_ERR_INVALID_ARG;
    return bus->ops->read_reg(bus->ctx, reg, data, len);
}

static inline bus_status_t bus_write_reg(const bus_interface_t *bus, uint16_t reg, const uint8_t *data, size_t len) {
    if (!bus || !bus->ops || !bus->ops->write_reg) return BUS_ERR_INVALID_ARG;
    return bus->ops->write_reg(bus->ctx, reg, data, len);
}

static inline bus_status_t bus_read_u8(const bus_interface_t *bus, uint16_t reg, uint8_t *val) {
    return bus_read_reg(bus, reg, val, 1);
}

static inline bus_status_t bus_write_u8(const bus_interface_t *bus, uint16_t reg, uint8_t val) {
    return bus_write_reg(bus, reg, &val, 1);
}

/**
 * @brief Атомарна модифікація бітів регістра (Read-Modify-Write).
 */
bus_status_t bus_modify_reg(const bus_interface_t *bus, uint16_t reg, uint8_t mask, uint8_t val);

#ifdef __cplusplus
}
#endif

#endif /* BUS_TRANSACTION_H_ */
