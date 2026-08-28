#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UART_RX_DMA_BUF_SIZE   512
#define UART_TX_RING_BUF_SIZE  1024
#define MAVLINK_MAX_PACKET_LEN 280

/* Рівні пріоритету повідомлень для політики скидання при заторах */
typedef enum {
    PKT_PRIORITY_LOW = 0,     /* Потокова телеметрія: ATTITUDE, VFR_HUD */
    PKT_PRIORITY_MEDIUM = 1,  /* Навігація: GLOBAL_POSITION_INT, GPS_RAW_INT */
    PKT_PRIORITY_HIGH = 2     /* Критичні кадри: HEARTBEAT, COMMAND_ACK, PARAM_VALUE */
} packet_priority_t;

/* Кільцевий буфер передачі (SPSC: Single-Producer Single-Consumer) */
typedef struct {
    uint8_t buffer[UART_TX_RING_BUF_SIZE];
    volatile uint16_t head;          /* Індекс запису (модифікує продюсер) */
    volatile uint16_t tail;          /* Індекс читання (модифікує DMA ISR) */
    uint32_t dropped_packets;        /* Лічильник скинутих пакетів */
    uint32_t total_sent_bytes;       /* Загальна кількість переданих байтів */
} tx_ring_buffer_t;

/* Структура контексту драйвера UART */
typedef struct {
    uint8_t dma_rx_buf[UART_RX_DMA_BUF_SIZE];
    uint16_t last_rx_index;
    tx_ring_buffer_t tx_ring;
    volatile bool tx_dma_busy;
} mavlink_uart_driver_t;

static mavlink_uart_driver_t g_mav_driver;

/* Ініціалізація структури драйвера */
void mavlink_driver_init(mavlink_uart_driver_t *drv) {
    memset(drv, 0, sizeof(mavlink_uart_driver_t));
    drv->last_rx_index = 0;
    drv->tx_dma_busy = false;
    drv->tx_ring.head = 0;
    drv->tx_ring.tail = 0;
    drv->tx_ring.dropped_packets = 0;
    drv->tx_ring.total_sent_bytes = 0;
}

/* Обчислення кількості вільних байтів у передавальному кільці */
static inline uint16_t tx_ring_available(const tx_ring_buffer_t *rb) {
    uint16_t head = rb->head;
    uint16_t tail = rb->tail;
    if (head >= tail) {
        return (UART_TX_RING_BUF_SIZE - 1) - (head - tail);
    }
    return tail - head - 1;
}

/* Запуск апаратного каналу DMA TX на неперервний блок пам'яті */
static void start_dma_tx_transfer(mavlink_uart_driver_t *drv) {
    if (drv->tx_dma_busy) {
        return;
    }

    uint16_t head = drv->tx_ring.head;
    uint16_t tail = drv->tx_ring.tail;

    if (head == tail) {
        return; /* Буфер порожній */
    }

    uint16_t chunk_len = 0;
    if (head > tail) {
        chunk_len = head - tail;
    } else {
        /* Дані переходять через фізичний кінець масиву */
        chunk_len = UART_TX_RING_BUF_SIZE - tail;
    }

    drv->tx_dma_busy = true;

    /* Виклик апаратного рівня (HAL/LL мікроконтролера):
       HAL_UART_Transmit_DMA(&huart1, &drv->tx_ring.buffer[tail], chunk_len); */
}

/* Неблокувальне додавання пакета MAVLink у передавальний буфер */
bool mavlink_uart_send_packet(mavlink_uart_driver_t *drv, 
                              const uint8_t *packet, 
                              uint16_t len, 
                              packet_priority_t prio) {
    if (len == 0 || len > MAVLINK_MAX_PACKET_LEN) {
        return false;
    }

    uint16_t free_space = tx_ring_available(&drv->tx_ring);

    /* Якщо місця бракує, застосовуємо політику скидання за пріоритетом */
    if (free_space < len) {
        if (prio == PKT_PRIORITY_LOW || prio == PKT_PRIORITY_MEDIUM) {
            drv->tx_ring.dropped_packets++;
            return false; /* Безпечно відкидаємо надлишкову телеметрію */
        }
        /* Для високопріоритетного пакета перевіряємо критичний поріг */
        if (free_space < len) {
            drv->tx_ring.dropped_packets++;
            return false;
        }
    }

    /* Послідовний запис байтів у кільцевий буфер */
    uint16_t head = drv->tx_ring.head;
    for (uint16_t i = 0; i < len; ++i) {
        drv->tx_ring.buffer[head] = packet[i];
        head = (head + 1) % UART_TX_RING_BUF_SIZE;
    }
    drv->tx_ring.head = head;

    /* Запускаємо передачу DMA, якщо передавач був вільний */
    start_dma_tx_transfer(drv);
    return true;
}

/* Обробник переривання завершення передачі DMA (TX Complete ISR) */
void DMA1_Channel_UART_TX_IRQHandler(void) {
    mavlink_uart_driver_t *drv = &g_mav_driver;

    /* У реальній системі передана довжина chunk_len фіксується при старті */
    /* Оновлюємо tail кільцевого буфера на передану довжину */
    drv->tx_dma_busy = false;

    /* Запускаємо наступний фрагмент, якщо в буфері ще залишилися дані */
    start_dma_tx_transfer(drv);
}

/* Обробник апаратного переривання простою лінії UART IDLE (новий пакет надійшов) */
void UART_RX_IdleLine_IRQHandler(mavlink_uart_driver_t *drv, void (*byte_parser)(uint8_t byte)) {
    /* Зчитуємо поточну позицію запису з лічильника регістра DMA:
       uint16_t current_pos = UART_RX_DMA_BUF_SIZE - __HAL_DMA_GET_COUNTER(huart->hdmarx); */
    uint16_t current_pos = 128; /* Приклад значення з регістра */
    uint16_t last_pos = drv->last_rx_index;

    if (current_pos != last_pos) {
        if (current_pos > last_pos) {
            /* Неперервний лінійний сегмент */
            for (uint16_t i = last_pos; i < current_pos; ++i) {
                byte_parser(drv->dma_rx_buf[i]);
            }
        } else {
            /* Кільце перейшло через кінець фізичного масиву */
            for (uint16_t i = last_pos; i < UART_RX_DMA_BUF_SIZE; ++i) {
                byte_parser(drv->dma_rx_buf[i]);
            }
            for (uint16_t i = 0; i < current_pos; ++i) {
                byte_parser(drv->dma_rx_buf[i]);
            }
        }
        drv->last_rx_index = current_pos;
    }
}
