/* ============================================================================
 * ФАЙЛ: driver_core.c - Повна реалізація каркаса драйвера на C99
 * ============================================================================ */
#include "driver_core.h"
#include <string.h>

#define DRIVER_MAGIC            0x44525631U /* "DRV1" */
#define MAX_INSTANCES           4
#define TRANSACTION_QUEUE_SIZE  8

/* Регістрова карта (Memory-Mapped Hardware Registers або Mock) */
typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t DR;
    volatile uint32_t SR1;
    volatile uint32_t SR2;
    volatile uint32_t CCR;
    volatile uint32_t TRISE;
} hw_i2c_registers_t;

/* Бітові маски статусів */
#define SR1_SB      (1U << 0)
#define SR1_ADDR    (1U << 1)
#define SR1_BTF     (1U << 2)
#define SR1_RXNE    (1U << 6)
#define SR1_TXE     (1U << 7)
#define SR1_AF      (1U << 10) /* Acknowledge Failure (NACK) */
#define SR1_TIMEOUT (1U << 14)

/* Стани кінцевого автомата */
typedef enum {
    STATE_UNINITIALIZED = 0,
    STATE_IDLE,
    STATE_BUSY_TX,
    STATE_BUSY_RX,
    STATE_RECOVERY,
    STATE_ERROR
} driver_state_t;

/* Внутрішня структура дескриптора */
struct driver_instance_s {
    uint32_t magic;
    uint8_t port_id;
    hw_i2c_registers_t* regs;
    driver_config_t config;
    volatile driver_state_t state;

    /* Черга транзакцій */
    driver_transaction_t queue[TRANSACTION_QUEUE_SIZE];
    volatile size_t queue_head;
    volatile size_t queue_tail;
    volatile size_t queue_count;

    /* Поточна активна транзакція */
    driver_transaction_t current_trans;
    volatile size_t tx_idx;
    volatile size_t rx_idx;
    volatile uint32_t start_time_us;

    /* Статистика */
    driver_stats_t stats;
};

static struct driver_instance_s s_instances[MAX_INSTANCES];
static bool s_instances_allocated[MAX_INSTANCES] = {false};

/* Хелпери для критичних секцій */
static inline uint32_t enter_critical(void) {
    /* На реальному ARM Cortex-M: primask = __get_PRIMASK(); __disable_irq(); return primask; */
    return 0;
}

static inline void exit_critical(uint32_t primask) {
    (void)primask;
    /* На реальному ARM Cortex-M: __set_PRIMASK(primask); */
}

/* Отримання поточного часу в мікросекундах (емуляція або DWT) */
static inline uint32_t get_time_us(void) {
    static uint32_t fake_us = 0;
    return ++fake_us;
}

driver_handle_t driver_create(uint8_t port_id, void* reg_base, const driver_config_t* config) {
    if (port_id >= MAX_INSTANCES || reg_base == NULL || config == NULL) {
        return NULL;
    }
    if (s_instances_allocated[port_id]) {
        return &s_instances[port_id];
    }

    driver_handle_t h = &s_instances[port_id];
    memset(h, 0, sizeof(*h));
    h->magic = DRIVER_MAGIC;
    h->port_id = port_id;
    h->regs = (hw_i2c_registers_t*)reg_base;
    h->config = *config;
    h->state = STATE_UNINITIALIZED;

    s_instances_allocated[port_id] = true;
    return h;
}

driver_status_t driver_init(driver_handle_t h) {
    if (h == NULL || h->magic != DRIVER_MAGIC) return DRIVER_ERR_INVALID_PARAM;

    uint32_t cs = enter_critical();
    h->regs->CR1 = 0; /* Скидання модуля */
    h->regs->CCR = (h->config.clock_hz >= 400000) ? 0x8028 : 0x0050;
    h->regs->CR1 = 1; /* PE = 1 (Peripheral Enable) */

    h->queue_head = 0;
    h->queue_tail = 0;
    h->queue_count = 0;
    h->state = STATE_IDLE;
    exit_critical(cs);

    return DRIVER_OK;
}

static void start_next_transaction_internal(driver_handle_t h) {
    if (h->queue_count == 0) {
        h->state = STATE_IDLE;
        return;
    }

    h->current_trans = h->queue[h->queue_tail];
    h->queue_tail = (h->queue_tail + 1) % TRANSACTION_QUEUE_SIZE;
    h->queue_count--;

    h->tx_idx = 0;
    h->rx_idx = 0;
    h->start_time_us = get_time_us();

    if (h->current_trans.op_type == DRIVER_OP_WRITE ||
        h->current_trans.op_type == DRIVER_OP_WRITE_READ) {
        h->state = STATE_BUSY_TX;
    } else {
        h->state = STATE_BUSY_RX;
    }

    h->stats.total_transfers++;

    /* Апаратна генерація START умови */
    h->regs->CR1 |= (1U << 8); /* START = 1 */
}

driver_status_t driver_submit_async(driver_handle_t h, const driver_transaction_t* trans) {
    if (h == NULL || h->magic != DRIVER_MAGIC) return DRIVER_ERR_INVALID_PARAM;
    if (h->state == STATE_UNINITIALIZED) return DRIVER_ERR_UNINITIALIZED;
    if (trans == NULL) return DRIVER_ERR_INVALID_PARAM;

    uint32_t cs = enter_critical();
    if (h->queue_count >= TRANSACTION_QUEUE_SIZE) {
        exit_critical(cs);
        return DRIVER_ERR_OVERFLOW;
    }

    h->queue[h->queue_head] = *trans;
    h->queue_head = (h->queue_head + 1) % TRANSACTION_QUEUE_SIZE;
    h->queue_count++;

    if (h->state == STATE_IDLE) {
        start_next_transaction_internal(h);
    }
    exit_critical(cs);

    return DRIVER_OK;
}

void driver_poll_isr(driver_handle_t h) {
    if (h == NULL || h->state == STATE_IDLE || h->state == STATE_UNINITIALIZED) return;

    uint32_t sr1 = h->regs->SR1;

    /* 1. Перевірка помилки NACK */
    if (sr1 & SR1_AF) {
        h->regs->SR1 &= ~SR1_AF;   /* Очищення прапорця */
        h->regs->CR1 |= (1U << 9); /* STOP = 1 */
        h->stats.nack_errors++;

        if (h->current_trans.callback) {
            h->current_trans.callback(h, DRIVER_ERR_NACK, h->tx_idx, h->current_trans.user_data);
        }
        start_next_transaction_internal(h);
        return;
    }

    /* 2. Обробка передачі байтів (TX) */
    if (h->state == STATE_BUSY_TX) {
        if (sr1 & SR1_SB) {
            /* Передача адреси з бітом запису (W=0) */
            h->regs->DR = (uint32_t)(h->current_trans.dev_addr << 1);
        } else if (sr1 & SR1_ADDR) {
            /* Очищення прапорця ADDR читанням SR2 */
            volatile uint32_t dummy = h->regs->SR2;
            (void)dummy;
        } else if (sr1 & SR1_TXE) {
            if (h->tx_idx < h->current_trans.tx_len) {
                h->regs->DR = h->current_trans.tx_buf[h->tx_idx++];
            } else if (sr1 & SR1_BTF) {
                if (h->current_trans.op_type == DRIVER_OP_WRITE_READ) {
                    /* Перехід до фази читання через повторний старт */
                    h->state = STATE_BUSY_RX;
                    h->regs->CR1 |= (1U << 8); /* RESTART = 1 */
                } else {
                    /* Завершення передачі */
                    h->regs->CR1 |= (1U << 9); /* STOP = 1 */
                    h->stats.successful_transfers++;
                    if (h->current_trans.callback) {
                        h->current_trans.callback(h, DRIVER_OK, h->tx_idx, h->current_trans.user_data);
                    }
                    start_next_transaction_internal(h);
                }
            }
        }
    }
    /* 3. Обробка прийому байтів (RX) */
    else if (h->state == STATE_BUSY_RX) {
        if (sr1 & SR1_SB) {
            /* Передача адреси з бітом читання (R=1) */
            h->regs->DR = (uint32_t)((h->current_trans.dev_addr << 1) | 1U);
        } else if (sr1 & SR1_ADDR) {
            volatile uint32_t dummy = h->regs->SR2;
            (void)dummy;
        } else if (sr1 & SR1_RXNE) {
            if (h->rx_idx < h->current_trans.rx_len) {
                h->current_trans.rx_buf[h->rx_idx++] = (uint8_t)h->regs->DR;
            }
            if (h->rx_idx >= h->current_trans.rx_len) {
                h->regs->CR1 |= (1U << 9); /* STOP = 1 */
                h->stats.successful_transfers++;
                if (h->current_trans.callback) {
                    h->current_trans.callback(h, DRIVER_OK, h->rx_idx, h->current_trans.user_data);
                }
                start_next_transaction_internal(h);
            }
        }
    }
}

driver_status_t driver_reset_bus(driver_handle_t h) {
    if (h == NULL || h->magic != DRIVER_MAGIC) return DRIVER_ERR_INVALID_PARAM;

    uint32_t cs = enter_critical();
    h->state = STATE_RECOVERY;
    h->stats.bus_recoveries++;

    /* 1. Програмне скидання блока */
    h->regs->CR1 = 0x8000; /* SWRST = 1 */
    for (volatile int i = 0; i < 100; i++) asm volatile("nop");
    h->regs->CR1 = 0;      /* SWRST = 0 */

    /* 2. Відновлення налаштувань */
    driver_init(h);
    exit_critical(cs);

    return DRIVER_OK;
}

driver_status_t driver_get_stats(driver_handle_t h, driver_stats_t* stats) {
    if (h == NULL || stats == NULL || h->magic != DRIVER_MAGIC) return DRIVER_ERR_INVALID_PARAM;
    *stats = h->stats;
    return DRIVER_OK;
}
