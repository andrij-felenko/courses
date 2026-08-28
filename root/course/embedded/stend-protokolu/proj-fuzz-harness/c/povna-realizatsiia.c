#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>

#define FRAME_MAGIC_BYTE 0xAA
#define MAX_PAYLOAD_SIZE 64
#define HEADER_SIZE      3 /* Magic(1B) + MsgType(1B) + PayloadLen(1B) */
#define CRC_SIZE         2

typedef struct {
    uint8_t msg_type;
    uint8_t payload_len;
    uint8_t payload[MAX_PAYLOAD_SIZE];
    uint16_t crc16;
} DecodedFrame_t;

/* Обчислення контрольної суми CRC-16/CCITT-FALSE (поліном 0x1021) */
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/* 
 * Функція розбору сирого потоку байтів.
 * Шукає маркер 0xAA, перевіряє межі буфера та валідує контрольну суму.
 * Повертає true, якщо знайдено та успішно декодовано валідний кадр.
 */
bool parse_raw_stream(const uint8_t *data, size_t size, DecodedFrame_t *out_frame) {
    if (data == NULL || size < (HEADER_SIZE + CRC_SIZE) || out_frame == NULL) {
        return false;
    }

    size_t cursor = 0;
    while (cursor < size) {
        /* 1. Пошук маркера початку кадру */
        if (data[cursor] != FRAME_MAGIC_BYTE) {
            cursor++;
            continue;
        }

        /* 2. Перевірка, чи доступний повний заголовок */
        if (cursor + HEADER_SIZE > size) {
            break;
        }

        uint8_t msg_type = data[cursor + 1];
        uint8_t payload_len = data[cursor + 2];

        /* 3. Захист від некоректного розміру корисного навантаження */
        if (payload_len > MAX_PAYLOAD_SIZE) {
            cursor++;
            continue;
        }

        size_t total_frame_len = HEADER_SIZE + (size_t)payload_len + CRC_SIZE;
        if (cursor + total_frame_len > size) {
            /* Кадр неповний — очікуємо надходження решти байтів */
            break;
        }

        /* 4. Вилучення та перевірка контрольної суми CRC-16 */
        size_t crc_offset = cursor + HEADER_SIZE + payload_len;
        uint16_t expected_crc = (uint16_t)data[crc_offset] |
                                ((uint16_t)data[crc_offset + 1] << 8);

        uint16_t calculated_crc = crc16_ccitt(&data[cursor + 1], (size_t)HEADER_SIZE - 1 + payload_len);

        if (calculated_crc == expected_crc) {
            out_frame->msg_type = msg_type;
            out_frame->payload_len = payload_len;
            if (payload_len > 0) {
                memcpy(out_frame->payload, &data[cursor + HEADER_SIZE], payload_len);
            }
            out_frame->crc16 = expected_crc;
            return true;
        }

        /* CRC не зійшлася — продовжуємо пошук наступного маркера 0xAA */
        cursor++;
    }

    return false;
}

/* Обов'язкова точка входу для LLVM LibFuzzer */
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    DecodedFrame_t frame;
    memset(&frame, 0, sizeof(frame));
    
    /* Передаємо згенеровані мутатором байти у тестовану функцію розбору */
    parse_raw_stream(data, size, &frame);
    
    return 0; /* 0 сигналізує фазеру про успішну обробку входу */
}
