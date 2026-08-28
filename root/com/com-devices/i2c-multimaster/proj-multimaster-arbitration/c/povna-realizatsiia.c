#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#define I2C_MAX_BUFFER_SIZE      32
#define I2C_MAX_RETRIES          5
#define I2C_BASE_BACKOFF_US      100

typedef enum {
    I2C_STATE_IDLE = 0,
    I2C_STATE_MASTER_TX,
    I2C_STATE_MASTER_RX,
    I2C_STATE_SLAVE_TX,
    I2C_STATE_SLAVE_RX,
    I2C_STATE_ARBITRATION_LOST,
    I2C_STATE_ERROR
} i2c_bus_state_t;

typedef enum {
    I2C_STATUS_OK = 0,
    I2C_STATUS_BUSY,
    I2C_STATUS_ARBITRATION_LOST,
    I2C_STATUS_NACK,
    I2C_STATUS_TIMEOUT,
    I2C_STATUS_OVERFLOW
} i2c_status_t;

/* Дескриптор повідомлення I2C */
typedef struct {
    uint8_t target_address;
    uint8_t buffer[I2C_MAX_BUFFER_SIZE];
    size_t  length;
    size_t  transferred;
    bool    is_read;
    uint8_t retry_count;
} i2c_transaction_t;

/* Структура контексту драйвера багатомайстрового I2C */
typedef struct {
    volatile i2c_bus_state_t state;
    uint8_t                  own_address;
    i2c_transaction_t        active_msg;
    
    /* Буфер веденого для прийому запитів від інших ведучих */
    uint8_t                  slave_rx_buf[I2C_MAX_BUFFER_SIZE];
    size_t                   slave_rx_len;
    
    /* Колбек обробки даних, отриманих у режимі веденого */
    void (*slave_rx_callback)(const uint8_t *data, size_t len);
    
    /* Лічильники статистики */
    uint32_t                 arlo_count;
    uint32_t                 tx_success_count;
    uint32_t                 rx_success_count;
} i2c_multimaster_driver_t;

static i2c_multimaster_driver_t g_i2c_drv;

/* Псевдоапаратні функції доступу до регістрів контролера */
extern void hw_i2c_generate_start(void);
extern void hw_i2c_generate_stop(void);
extern void hw_i2c_write_byte(uint8_t byte);
extern uint8_t hw_i2c_read_byte(void);
extern void hw_i2c_enable_ack(bool enable);
extern void hw_i2c_clear_arlo_flag(void);
extern void hw_i2c_disable_tx_interrupts(void);
extern void hw_i2c_enable_slave_listening(uint8_t own_addr);
extern void hw_delay_us(uint32_t us);

/* Генерація випадкового відступу за алгоритмом Exponential Backoff */
static uint32_t calculate_backoff_delay_us(uint8_t retry_count) {
    if (retry_count > I2C_MAX_RETRIES) {
        retry_count = I2C_MAX_RETRIES;
    }
    uint32_t max_slots = (1U << retry_count);
    uint32_t random_slot = (uint32_t)rand() % max_slots;
    return (random_slot + 1) * I2C_BASE_BACKOFF_US;
}

/* Ініціалізація драйвера з власною адресою веденого */
void i2c_multimaster_init(uint8_t own_address, void (*rx_cb)(const uint8_t *, size_t)) {
    g_i2c_drv.state = I2C_STATE_IDLE;
    g_i2c_drv.own_address = own_address;
    g_i2c_drv.slave_rx_callback = rx_cb;
    g_i2c_drv.arlo_count = 0;
    g_i2c_drv.tx_success_count = 0;
    g_i2c_drv.rx_success_count = 0;
    g_i2c_drv.active_msg.length = 0;
    
    hw_i2c_enable_slave_listening(own_address);
}

/* Спроба передачі пакета ведучим */
i2c_status_t i2c_multimaster_transmit(uint8_t target_addr, const uint8_t *data, size_t len) {
    if (len > I2C_MAX_BUFFER_SIZE || len == 0) {
        return I2C_STATUS_OVERFLOW;
    }
    if (g_i2c_drv.state != I2C_STATE_IDLE) {
        return I2C_STATUS_BUSY;
    }

    g_i2c_drv.active_msg.target_address = target_addr;
    g_i2c_drv.active_msg.length = len;
    g_i2c_drv.active_msg.transferred = 0;
    g_i2c_drv.active_msg.is_read = false;
    g_i2c_drv.active_msg.retry_count = 0;
    
    for (size_t i = 0; i < len; ++i) {
        g_i2c_drv.active_msg.buffer[i] = data[i];
    }

    g_i2c_drv.state = I2C_STATE_MASTER_TX;
    hw_i2c_generate_start();
    return I2C_STATUS_OK;
}

/* Обробник переривання подій I2C (Event ISR) */
void I2C_EV_IRQHandler(void) {
    switch (g_i2c_drv.state) {
        case I2C_STATE_MASTER_TX:
            /* Подія: START надіслано -> передаємо адресу з бітом W (0) */
            if (g_i2c_drv.active_msg.transferred == 0) {
                uint8_t addr_byte = (g_i2c_drv.active_msg.target_address << 1) | 0x00;
                hw_i2c_write_byte(addr_byte);
                g_i2c_drv.active_msg.transferred = 1;
            } else {
                size_t byte_idx = g_i2c_drv.active_msg.transferred - 1;
                if (byte_idx < g_i2c_drv.active_msg.length) {
                    hw_i2c_write_byte(g_i2c_drv.active_msg.buffer[byte_idx]);
                    g_i2c_drv.active_msg.transferred++;
                } else {
                    /* Усі байти передано -> формуємо STOP */
                    hw_i2c_generate_stop();
                    g_i2c_drv.state = I2C_STATE_IDLE;
                    g_i2c_drv.tx_success_count++;
                }
            }
            break;

        case I2C_STATE_SLAVE_RX:
            /* Подія: отримано байт у режимі веденого */
            if (g_i2c_drv.slave_rx_len < I2C_MAX_BUFFER_SIZE) {
                g_i2c_drv.slave_rx_buf[g_i2c_drv.slave_rx_len++] = hw_i2c_read_byte();
            }
            break;

        default:
            break;
    }
}

/* Обробник переривання виявлення власної адреси (Match ADDR ISR) */
void I2C_ADDR_Match_IRQHandler(void) {
    /* Інший ведучий звернувся до нас */
    g_i2c_drv.state = I2C_STATE_SLAVE_RX;
    g_i2c_drv.slave_rx_len = 0;
    hw_i2c_enable_ack(true);
}

/* Обробник завершення передачі чужого пакета (STOPF ISR) */
void I2C_STOPF_IRQHandler(void) {
    if (g_i2c_drv.state == I2C_STATE_SLAVE_RX) {
        if (g_i2c_drv.slave_rx_callback && g_i2c_drv.slave_rx_len > 0) {
            g_i2c_drv.slave_rx_callback(g_i2c_drv.slave_rx_buf, g_i2c_drv.slave_rx_len);
        }
        g_i2c_drv.rx_success_count++;
        g_i2c_drv.state = I2C_STATE_IDLE;
    }
}

/* Обробник переривання помилок та колізій (Error ISR) */
void I2C_ER_IRQHandler(void) {
    /* 1. Перевіряємо біт втрати арбітражу ARLO */
    g_i2c_drv.arlo_count++;
    hw_i2c_clear_arlo_flag();
    hw_i2c_disable_tx_interrupts();
    
    g_i2c_drv.state = I2C_STATE_ARBITRATION_LOST;
    
    /* 2. Залишаємо ведений режим увімкненим: перевіряємо, чи не викликають нас */
    hw_i2c_enable_slave_listening(g_i2c_drv.own_address);
    
    /* 3. Плануємо повторну спробу, якщо не вичерпано ліміт */
    if (g_i2c_drv.active_msg.retry_count < I2C_MAX_RETRIES) {
        g_i2c_drv.active_msg.retry_count++;
        uint32_t backoff_us = calculate_backoff_delay_us(g_i2c_drv.active_msg.retry_count);
        hw_delay_us(backoff_us);
        
        /* Скидаємо індекс переданих байтів для повного рестарту */
        g_i2c_drv.active_msg.transferred = 0;
        g_i2c_drv.state = I2C_STATE_MASTER_TX;
        hw_i2c_generate_start();
    } else {
        /* Ліміт повторів вичерпано -> перехід у спокій */
        g_i2c_drv.state = I2C_STATE_IDLE;
    }
}
