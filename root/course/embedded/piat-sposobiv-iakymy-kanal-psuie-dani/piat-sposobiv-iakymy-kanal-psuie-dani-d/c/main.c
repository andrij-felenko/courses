// Повний модульний конвеєр надійного канального приймача на C99
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define LINK_MAX_PAYLOAD      128U
#define LINK_HEADER_SIZE      1U   // 1 байт Sequence Number
#define LINK_CRC_SIZE         2U   // 2 байти CRC-16
#define LINK_MAX_FRAME_SIZE   (LINK_HEADER_SIZE + LINK_MAX_PAYLOAD + LINK_CRC_SIZE)
#define LINK_COBS_MAX_SIZE    (LINK_MAX_FRAME_SIZE + (LINK_MAX_FRAME_SIZE / 254U) + 2U)
#define LINK_FRAME_DELIMITER  0x00U

// Статуси результату конвеєра
typedef enum {
    LINK_OK = 0,
    LINK_FRAME_PENDING,
    LINK_ERR_BUFFER_OVERFLOW,
    LINK_ERR_COBS_CORRUPTED,
    LINK_ERR_CRC_MISMATCH,
    LINK_ERR_DUPLICATE_FRAME
} link_status_t;

// Тип функції зворотного виклику для передачі валідного корисного навантаження
typedef void (*link_payload_handler_t)(const uint8_t *payload, size_t len, void *user_ctx);
// Тип функції відправки ACK-квитанцій
typedef void (*link_ack_sender_t)(uint8_t seq_num, void *user_ctx);

// Контекст стану приймача
typedef struct {
    uint8_t rx_raw_buf[LINK_COBS_MAX_SIZE];
    size_t  rx_raw_idx;
    uint8_t decode_buf[LINK_MAX_FRAME_SIZE + 2U];
    uint8_t expected_seq;
    link_payload_handler_t on_payload;
    link_ack_sender_t      send_ack;
    void                  *user_ctx;
} link_receiver_t;

// Обчислення CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF)
uint16_t link_crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= ((uint16_t)data[i]) << 8U;
        for (uint8_t bit = 0; bit < 8U; ++bit) {
            if (crc & 0x8000U) {
                crc = (crc << 1U) ^ 0x1021U;
            } else {
                crc = crc << 1U;
            }
        }
    }
    return crc;
}

// Декодування COBS у вихідний двійковий масив
static bool link_cobs_decode(const uint8_t *src, size_t src_len, uint8_t *dst, size_t *dst_len) {
    if (src_len == 0 || src == NULL || dst == NULL) {
        return false;
    }
    
    size_t src_idx = 0;
    size_t dst_idx = 0;
    
    while (src_idx < src_len) {
        uint8_t code = src[src_idx++];
        if (code == 0) {
            return false; // Нуль всередині тіла COBS неприпустимий
        }
        
        for (uint8_t i = 1; i < code; ++i) {
            if (src_idx >= src_len) {
                return false; // Вихід покажчика за межі вхідних даних
            }
            dst[dst_idx++] = src[src_idx++];
        }
        
        if (code < 0xFFU && src_idx < src_len) {
            dst[dst_idx++] = 0x00U; // Відновлюємо замінений нуль
        }
    }
    
    *dst_len = dst_idx;
    return true;
}

// Ініціалізація приймача
void link_receiver_init(link_receiver_t *rx,
                        link_payload_handler_t on_payload,
                        link_ack_sender_t send_ack,
                        void *user_ctx) {
    memset(rx, 0, sizeof(*rx));
    rx->expected_seq = 0U;
    rx->on_payload = on_payload;
    rx->send_ack = send_ack;
    rx->user_ctx = user_ctx;
}

// Обробка одного отриманого байта з фізичного інтерфейсу (UART/DMA)
link_status_t link_receiver_feed_byte(link_receiver_t *rx, uint8_t byte) {
    // 1. Пошук демаркатора меж кадру 0x00
    if (byte == LINK_FRAME_DELIMITER) {
        if (rx->rx_raw_idx == 0) {
            return LINK_FRAME_PENDING; // Порожній кадр між послідовними нулями
        }
        
        size_t decoded_len = 0;
        // 2. COBS-декодування кадру
        if (!link_cobs_decode(rx->rx_raw_buf, rx->rx_raw_idx, rx->decode_buf, &decoded_len)) {
            rx->rx_raw_idx = 0;
            return LINK_ERR_COBS_CORRUPTED;
        }
        rx->rx_raw_idx = 0; // Скидаємо буфер для наступного кадру
        
        // Кадр мусить містити щонайменше 1Б Seq + 2Б CRC
        if (decoded_len < (LINK_HEADER_SIZE + LINK_CRC_SIZE)) {
            return LINK_ERR_CRC_MISMATCH;
        }
        
        // 3. Перевірка контрольної суми CRC-16
        uint16_t calculated_crc = link_crc16_ccitt(rx->decode_buf, decoded_len - LINK_CRC_SIZE);
        uint16_t received_crc = ((uint16_t)rx->decode_buf[decoded_len - 2U] << 8U) |
                                ((uint16_t)rx->decode_buf[decoded_len - 1U]);
                                
        if (calculated_crc != received_crc) {
            return LINK_ERR_CRC_MISMATCH;
        }
        
        // 4. Перевірка порядкового номера та дедуплікація
        uint8_t seq_num = rx->decode_buf[0];
        if (rx->send_ack != NULL) {
            rx->send_ack(seq_num, rx->user_ctx); // Квитуємо отримання
        }
        
        if (seq_num != rx->expected_seq) {
            // Це дублікат уже прийнятого раніше кадру!
            return LINK_ERR_DUPLICATE_FRAME;
        }
        
        // Оновлюємо очікуваний номер
        rx->expected_seq = (uint8_t)(rx->expected_seq + 1U);
        
        // 5. Передача корисного навантаження застосунку
        size_t payload_len = decoded_len - LINK_HEADER_SIZE - LINK_CRC_SIZE;
        if (rx->on_payload != NULL) {
            rx->on_payload(&rx->decode_buf[LINK_HEADER_SIZE], payload_len, rx->user_ctx);
        }
        
        return LINK_OK;
    }
    
    // Накопичення байтів у сирому буфері
    if (rx->rx_raw_idx >= LINK_COBS_MAX_SIZE) {
        rx->rx_raw_idx = 0; // Захист від переповнення при шумі
        return LINK_ERR_BUFFER_OVERFLOW;
    }
    
    rx->rx_raw_buf[rx->rx_raw_idx++] = byte;
    return LINK_FRAME_PENDING;
}
