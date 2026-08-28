/* ============================================================================
 * ФАЙЛ: driver_core.h - Публічний інтерфейс каркаса драйвера периферії
 * ============================================================================ */
#ifndef DRIVER_CORE_H
#define DRIVER_CORE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди повернення та статуси драйвера */
typedef enum {
    DRIVER_OK = 0,
    DRIVER_ERR_BUSY,
    DRIVER_ERR_TIMEOUT,
    DRIVER_ERR_NACK,
    DRIVER_ERR_BUS,
    DRIVER_ERR_OVERFLOW,
    DRIVER_ERR_INVALID_PARAM,
    DRIVER_ERR_UNINITIALIZED
} driver_status_t;

/* Типи операцій на послідовній шині */
typedef enum {
    DRIVER_OP_WRITE = 0,
    DRIVER_OP_READ,
    DRIVER_OP_WRITE_READ /* Repeated Start: запис регістра з наступним читанням */
} driver_op_type_t;

/* Непрозорий дескриптор екземпляра драйвера */
typedef struct driver_instance_s driver_instance_t;
typedef driver_instance_t* driver_handle_t;

/* Прототип функції зворотного виклику */
typedef void (*driver_callback_t)(driver_handle_t handle,
                                  driver_status_t status,
                                  size_t bytes_transferred,
                                  void* user_data);

/* Структура запиту на асинхронну транзакцію */
typedef struct {
    uint8_t dev_addr;              /* 7-бітна апаратна адреса пристрою */
    driver_op_type_t op_type;      /* Тип операції */
    const uint8_t* tx_buf;         /* Буфер передачі */
    size_t tx_len;                 /* Розмір буфера передачі */
    uint8_t* rx_buf;               /* Буфер прийому */
    size_t rx_len;                 /* Розмір буфера прийому */
    driver_callback_t callback;    /* Зворотний виклик після завершення */
    void* user_data;               /* Контекст користувача */
    uint32_t timeout_us;           /* Індивідуальний таймаут у мікросекундах */
} driver_transaction_t;

/* Незмінна конфігурація апаратного порту */
typedef struct {
    uint32_t clock_hz;             /* Тактова частота шини (100000 / 400000) */
    uint16_t default_timeout_ms;   /* Таймаут за замовчуванням */
    uint8_t sda_pin;               /* Номер піна даних */
    uint8_t scl_pin;               /* Номер піна тактування */
    uint8_t max_retries;           /* Кількість спроб повтору при NACK */
} driver_config_t;

/* Статистика та телеметрія екземпляра */
typedef struct {
    uint32_t total_transfers;
    uint32_t successful_transfers;
    uint32_t nack_errors;
    uint32_t timeout_errors;
    uint32_t bus_recoveries;
} driver_stats_t;

/* Публічні операції */
driver_handle_t driver_create(uint8_t port_id, void* reg_base, const driver_config_t* config);
driver_status_t driver_init(driver_handle_t handle);
driver_status_t driver_transfer_sync(driver_handle_t handle, const driver_transaction_t* trans);
driver_status_t driver_submit_async(driver_handle_t handle, const driver_transaction_t* trans);
void            driver_poll_isr(driver_handle_t handle); /* Викликається з ISR або super-loop */
driver_status_t driver_get_stats(driver_handle_t handle, driver_stats_t* stats);
driver_status_t driver_reset_bus(driver_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif /* DRIVER_CORE_H */
