/* Диспетчер шин: асинхронні транзакції I2C та SPI (чистий C HAL) */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    BUS_TYPE_I2C,
    BUS_TYPE_SPI
} bus_type_t;

typedef enum {
    BUS_DIR_WRITE,
    BUS_DIR_READ,
    BUS_DIR_WRITE_THEN_READ
} bus_direction_t;

typedef struct bus_transaction {
    bus_type_t      type;
    uint8_t         device_addr;     /* I2C 7-bit адреса або номер CS для SPI */
    uint8_t         reg_addr;        /* Внутрішній регістр чипа */
    const uint8_t  *tx_data;
    uint8_t        *rx_data;
    uint16_t        length;
    void          (*callback)(bool success, void *user_ctx);
    void           *user_ctx;
} bus_transaction_t;

#define BUS_QUEUE_SIZE 16
static bus_transaction_t s_queue[BUS_QUEUE_SIZE];
static volatile uint8_t  s_head = 0;
static volatile uint8_t  s_tail = 0;
static volatile bool     s_busy = false;

/* Постановка транзакції в неблокуючу чергу */
bool bus_submit_transaction(const bus_transaction_t *txn) {
    uint8_t next_head = (s_head + 1) % BUS_QUEUE_SIZE;
    if (next_head == s_tail) {
        return false; /* Черга переповнена */
    }
    s_queue[s_head] = *txn;
    s_head = next_head;

    /* Якщо шинний контролер вільний — запускаємо виконання */
    if (!s_busy) {
        bus_process_next();
    }
    return true;
}

/* Виконання наступної транзакції (викликається з головного циклу або ISR) */
void bus_process_next(void) {
    if (s_head == s_tail) {
        s_busy = false;
        return;
    }
    s_busy = true;
    bus_transaction_t *current = &s_queue[s_tail];

    if (current->type == BUS_TYPE_I2C) {
        /* Запуск апаратного I2C через DMA (псевдокод апаратного рівня) */
        // hal_i2c_master_mem_read_dma(current->device_addr, current->reg_addr, 
        //                             current->rx_data, current->length);
    } else if (current->type == BUS_TYPE_SPI) {
        /* Активація CS, запуск SPI DMA пересилки */
        // gpio_write_pin(current->device_addr, GPIO_LOW);
        // hal_spi_transmit_receive_dma(current->tx_data, current->rx_data, current->length);
    }
}

/* Обробник завершення DMA передачі */
void bus_dma_complete_isr(bool status) {
    if (s_head != s_tail) {
        bus_transaction_t *current = &s_queue[s_tail];
        if (current->callback) {
            current->callback(status, current->user_ctx);
        }
        s_tail = (s_tail + 1) % BUS_QUEUE_SIZE;
    }
    bus_process_next();
}
