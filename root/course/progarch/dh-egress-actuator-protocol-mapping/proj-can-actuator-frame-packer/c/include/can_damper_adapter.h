#ifndef CAN_DAMPER_ADAPTER_H
#define CAN_DAMPER_ADAPTER_H

#include "damper_actuator_port.h"
#include "can_frame_packer.h"

/**
 * @file can_damper_adapter.h
 * @brief Вихідний адаптер (Egress Adapter) сервоприводу заслінки для шини CAN.
 *
 * Адаптер імплементує інтерфейс доменного порту damper_actuator_port_t,
 * транслює доменні команди у кадри CAN, керує 4-бітним rolling counter,
 * викликає апаратний драйвер передачі та мапить помилки шини у доменні статуси.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди повернення абстрактного драйвера шини CAN.
 */
typedef enum {
    CAN_BUS_STATUS_OK = 0,              /**< Кадр успішно поміщено в чергу апаратного контролера */
    CAN_BUS_STATUS_TX_BUFFER_FULL = 1,  /**< Буфер відправки передавача переповнено */
    CAN_BUS_STATUS_BUS_OFF = 2,         /**< Контролер CAN перейшов у режим Bus-Off (апаратне відключення) */
    CAN_BUS_STATUS_TIMEOUT = 3,         /**< Перевищено час очікування арбітражу або відправки */
    CAN_BUS_STATUS_HARDWARE_ERROR = 4   /**< Загальний збій трансивера або контролера */
} can_bus_status_t;

/* Попереднє оголошення інтерфейсу драйвера шини CAN */
typedef struct can_bus_driver can_bus_driver_t;

/**
 * @brief Абстрактний інтерфейс драйвера шини CAN (SPI MCP2515, STM32 bxCAN, SocketCAN тощо).
 */
struct can_bus_driver {
    can_bus_status_t (*transmit)(can_bus_driver_t *self, const can_raw_frame_t *frame);
    void *driver_context;               /**< Контекст драйвера периферії */
};

/**
 * @brief Контекст вихідного адаптера сервоприводу заслінки.
 *
 * Першим полем містить базовий порт damper_actuator_port_t для безпечного приведення
 * вказівників в ідіоматичному C-поліморфізмі.
 */
typedef struct can_damper_adapter {
    damper_actuator_port_t  base_port;          /**< Доменний порт із vtable */
    can_bus_driver_t       *bus_driver;         /**< Покажчик на абстрактний драйвер шини CAN */
    uint32_t                can_id;             /**< CAN ID для передачі команд актуатора */
    uint8_t                 rolling_counter;    /**< Поточний стан 4-бітного лічильника [0..15] */
    bool                    is_initialized;     /**< Ознака готовності адаптера */
} can_damper_adapter_t;

/**
 * @brief Фабрична функція ініціалізації вихідного адаптера та прив'язки до шини.
 *
 * @param adapter     Вказівник на структуру екземпляра адаптера.
 * @param bus_driver  Вказівник на драйвер шини CAN.
 * @param can_id      Ідентифікатор CAN кадру керування.
 * @return Вказівник на екземпляр доменного порту damper_actuator_port_t,
 *         готового до передачі в доменне ядро.
 */
damper_actuator_port_t *can_damper_adapter_init(
    can_damper_adapter_t *adapter,
    can_bus_driver_t     *bus_driver,
    uint32_t              can_id
);

#ifdef __cplusplus
}
#endif

#endif /* CAN_DAMPER_ADAPTER_H */
