#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Публічний статус виконання операцій драйвера */
typedef enum {
    DRIVER_STATUS_OK = 0,
    DRIVER_STATUS_BUSY,
    DRIVER_STATUS_TIMEOUT,
    DRIVER_STATUS_NACK,
    DRIVER_STATUS_BUS_ERROR,
    DRIVER_STATUS_INVALID_PARAM
} driver_status_t;

/* Незмінна конфігурація апаратного інтерфейсу */
typedef struct {
    uint32_t clock_speed_hz;
    uint16_t timeout_ms;
    uint8_t sda_pin;
    uint8_t scl_pin;
    bool enable_dma;
} i2c_config_t;

/* Внутрішній стан машини транзакцій */
typedef enum {
    I2C_STATE_UNINITIALIZED = 0,
    I2C_STATE_IDLE,
    I2C_STATE_BUSY_TX,
    I2C_STATE_BUSY_RX,
    I2C_STATE_ERROR
} i2c_state_t;

/* Повна структура дескриптора екземпляра драйвера */
typedef struct i2c_handle_s {
    void* reg_base;                 /* Базова адреса регістрів периферії (I2C_TypeDef*) */
    i2c_config_t config;            /* Копія або посилання на конфігурацію */
    volatile i2c_state_t state;     /* Поточний стан драйвера */
    const uint8_t* tx_buffer;       /* Буфер передачі */
    volatile size_t tx_remaining;   /* Кількість байтів, що залишилося передати */
    uint8_t* rx_buffer;             /* Буфер прийому */
    volatile size_t rx_remaining;   /* Кількість байтів, що залишилося прийняти */
    uint32_t errors_count;          /* Лічильник зафіксованих апаратних збоїв */
} i2c_handle_t;

/* Ініціалізація конкретного екземпляра драйвера */
driver_status_t i2c_init(i2c_handle_t* handle, void* reg_base, const i2c_config_t* config);

/* Блокуюча синхронна транзакція запису */
driver_status_t i2c_master_write(i2c_handle_t* handle, uint8_t dev_addr,
                                 const uint8_t* data, size_t len);
