#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PROTOCOL_MAGIC_BYTE_0 0xAA
#define PROTOCOL_MAGIC_BYTE_1 0x55
#define CURRENT_MAJOR_VERSION 1
#define SUPPORTED_INCOMPAT_FLAGS_MASK 0x01 /* Підтримуємо лише прапорець 0x01 (наприклад, CRC-32) */

/* Заголовок кадру на дроті (8 байтів) */
typedef struct __attribute__((packed)) {
    uint8_t magic[2];      /* 0xAA, 0x55 */
    uint8_t ver_major;     /* Мажорна версія */
    uint8_t ver_minor;     /* Мінорна версія */
    uint8_t incompat_flags;/* Прапорці обов'язкової несумісності */
    uint8_t compat_flags;  /* Прапорці опційної сумісності */
    uint8_t msg_type;      /* Ідентифікатор типу повідомлення */
    uint8_t payload_len;   /* Довжина корисного навантаження в байтах */
} FrameHeader_t;

/* Типи повідомлень */
typedef enum {
    MSG_HEARTBEAT = 0x01,
    MSG_TELEMETRY = 0x02
} MsgType_t;

/* Структура повідомлення Telemetry поточної прошивки */
typedef struct {
    uint16_t voltage_mv;
    int32_t  current_ma;
    int16_t  temperature_c; /* Додано у версії 1.1 */
    bool     has_temperature;
} ParsedTelemetry_t;

/* Результати верифікації заголовка */
typedef enum {
    FRAME_VALID = 0,
    FRAME_ERR_BAD_MAGIC,
    FRAME_ERR_UNSUPPORTED_MAJOR,
    FRAME_ERR_UNKNOWN_INCOMPAT_FLAG,
    FRAME_ERR_LENGTH_OVERFLOW
} FrameVerifyResult_t;

/* 
 * 1. Низькорівнева валідація заголовка кадру.
 */
FrameVerifyResult_t verify_frame_header(const FrameHeader_t *hdr, size_t rx_buffer_size) {
    if (hdr->magic[0] != PROTOCOL_MAGIC_BYTE_0 || hdr->magic[1] != PROTOCOL_MAGIC_BYTE_1) {
        return FRAME_ERR_BAD_MAGIC;
    }
    
    /* Перевірка мажорної версії */
    if (hdr->ver_major != CURRENT_MAJOR_VERSION) {
        return FRAME_ERR_UNSUPPORTED_MAJOR;
    }
    
    /* Перевірка прапорців обов'язкової несумісності */
    if ((hdr->incompat_flags & ~SUPPORTED_INCOMPAT_FLAGS_MASK) != 0) {
        return FRAME_ERR_UNKNOWN_INCOMPAT_FLAG;
    }
    
    /* Перевірка, що весь пакет фізично поміщається в прийнятому буфері */
    if (sizeof(FrameHeader_t) + hdr->payload_len > rx_buffer_size) {
        return FRAME_ERR_LENGTH_OVERFLOW;
    }
    
    return FRAME_VALID;
}

/* 
 * 2. Диспетчеризація та розбір повідомлення Telemetry з підтримкою зміни полів.
 */
bool parse_msg_telemetry(const uint8_t *payload, uint8_t payload_len, ParsedTelemetry_t *out) {
    /* Мінімальний розмір версії 1.0: voltage_mv (2B) + current_ma (4B) = 6 байтів */
    if (payload_len < 6) {
        return false;
    }
    
    /* Розбір базових полів v1.0 за явними зміщеннями */
    out->voltage_mv = (uint16_t)(payload[0] | (payload[1] << 8));
    uint32_t raw_curr = (uint32_t)payload[2] | 
                        ((uint32_t)payload[3] << 8) | 
                        ((uint32_t)payload[4] << 16) | 
                        ((uint32_t)payload[5] << 24);
    out->current_ma = (int32_t)raw_curr;
    
    /* Перевірка наявності поля розширення v1.1 (temperature_c на зміщенні 6..7) */
    if (payload_len >= 8) {
        uint16_t raw_temp = (uint16_t)(payload[6] | (payload[7] << 8));
        out->temperature_c = (int16_t)raw_temp;
        out->has_temperature = true;
    } else {
        /* Пакет старого формату v1.0: виставляємо дефолт */
        out->temperature_c = 0;
        out->has_temperature = false;
    }
    
    return true;
}
