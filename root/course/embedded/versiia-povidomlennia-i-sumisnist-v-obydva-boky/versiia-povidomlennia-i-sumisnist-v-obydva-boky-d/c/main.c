#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PROTO_MAGIC_BYTE0       0xAA
#define PROTO_MAGIC_BYTE1       0x55
#define PROTO_SUPPORTED_MAJOR   1
#define TAG_CRITICAL_FLAG       0x80

// Бітові прапорці присутності полів у повідомленні
#define FIELD_FLAG_NODE_ID      (1U << 0)
#define FIELD_FLAG_TEMPERATURE  (1U << 1)
#define FIELD_FLAG_HUMIDITY     (1U << 2)
#define FIELD_FLAG_VOLTAGE      (1U << 3)
#define FIELD_FLAG_SOIL_EC      (1U << 4)
#define FIELD_FLAG_GPS          (1U << 5)

// Відомі числові теги схеми даних
typedef enum {
    TAG_NODE_ID     = 0x01,  // uint32_t (4 байти)
    TAG_TEMPERATURE = 0x02,  // int32_t  (4 байти, міліградуси Цельсія)
    TAG_HUMIDITY    = 0x03,  // uint16_t (2 байти, 0.01 %)
    TAG_VOLTAGE     = 0x04,  // uint16_t (2 байти, мілівольти)
    TAG_SOIL_EC     = 0x05,  // uint16_t (2 байти, мкСм/см, додано у v1.2)
    TAG_GPS_POS     = 0x06   // int32_t lat, int32_t lon (8 байтів, додано у v2.0)
} proto_tag_t;

// Коди результату роботи парсера
typedef enum {
    PARSE_OK = 0,
    PARSE_ERR_BUFFER_TOO_SMALL,
    PARSE_ERR_INVALID_MAGIC,
    PARSE_ERR_UNSUPPORTED_MAJOR_VERSION,
    PARSE_ERR_HEADER_CRC_MISMATCH,
    PARSE_ERR_PAYLOAD_TRUNCATED,
    PARSE_ERR_TAG_LENGTH_OVERFLOW,
    PARSE_ERR_TAG_VALUE_MALFORMED,
    PARSE_ERR_UNKNOWN_CRITICAL_TAG,
    PARSE_ERR_MANDATORY_FIELD_MISSING
} parse_status_t;

// Структура розібраного повідомлення
typedef struct {
    uint32_t node_id;
    int32_t  temperature_mc;    // міліградуси (-40000..+85000)
    uint16_t humidity_cpercent; // соті частки відсотка (0..10000)
    uint16_t battery_mv;        // мілівольти
    uint16_t soil_ec_us_cm;     // мікросименси на сантиметр
    int32_t  gps_latitude;      // 1e-7 градусів
    int32_t  gps_longitude;     // 1e-7 градусів

    uint32_t present_mask;          // маска розпізнаних полів
    uint16_t unknown_tags_skipped;  // кількість безпечно пропущених нових тегів
} telemetry_message_t;

// Проста перевірка CRC-8 для заголовка (поліном 0x07)
static uint8_t crc8_calc(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; ++b) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x07);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

// Безпечне читання Little-Endian без проблем з вирівнюванням пам'яті
static inline uint16_t read_u16_le(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static inline uint32_t read_u32_le(const uint8_t *p) {
    return (uint32_t)p[0]
         | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16)
         | ((uint32_t)p[3] << 24);
}

static inline int32_t read_i32_le(const uint8_t *p) {
    return (int32_t)read_u32_le(p);
}

// Головна функція відмовостійкого розбору пакета
parse_status_t parse_telemetry_packet(
    const uint8_t *buf,
    size_t buf_len,
    telemetry_message_t *out_msg
) {
    if (buf == NULL || out_msg == NULL) {
        return PARSE_ERR_BUFFER_TOO_SMALL;
    }

    // Мінімальний розмір заголовка: Magic(2) + Ver(1) + Seq(2) + PayloadLen(2) + HeaderCRC(1) = 8 байтів
    const size_t HEADER_SIZE = 8;
    if (buf_len < HEADER_SIZE) {
        return PARSE_ERR_BUFFER_TOO_SMALL;
    }

    // 1. Перевірка сигнатури (Magic)
    if (buf[0] != PROTO_MAGIC_BYTE0 || buf[1] != PROTO_MAGIC_BYTE1) {
        return PARSE_ERR_INVALID_MAGIC;
    }

    // 2. Перевірка контрольної суми заголовка (перші 7 байтів)
    uint8_t expected_header_crc = buf[7];
    if (crc8_calc(buf, 7) != expected_header_crc) {
        return PARSE_ERR_HEADER_CRC_MISMATCH;
    }

    // 3. Перевірка мажорної версії
    uint8_t version_byte = buf[2];
    uint8_t major_ver = (version_byte >> 4) & 0x0F;
    if (major_ver != PROTO_SUPPORTED_MAJOR) {
        return PARSE_ERR_UNSUPPORTED_MAJOR_VERSION;
    }

    // 4. Отримання розміру корисного навантаження
    uint16_t payload_len = read_u16_le(&buf[5]);
    if (buf_len < (HEADER_SIZE + (size_t)payload_len)) {
        return PARSE_ERR_PAYLOAD_TRUNCATED;
    }

    // 5. Ініціалізація вихідної структури дефолтними значеннями
    memset(out_msg, 0, sizeof(*out_msg));
    out_msg->temperature_mc = -999999; // позначка неініціалізованого сенсора

    // 6. Цикл потокового розбору TLV
    size_t cursor = HEADER_SIZE;
    const size_t payload_end = HEADER_SIZE + payload_len;

    while (cursor < payload_end) {
        // Кожен елемент TLV потребує щонайменше 2 байти (Tag + Length)
        if ((payload_end - cursor) < 2) {
            return PARSE_ERR_TAG_LENGTH_OVERFLOW;
        }

        uint8_t raw_tag = buf[cursor++];
        uint8_t tag_len = buf[cursor++];

        // Перевірка, чи не виходить тіло тегу за межі корисного навантаження
        if (tag_len > (payload_end - cursor)) {
            return PARSE_ERR_TAG_LENGTH_OVERFLOW;
        }

        const uint8_t *val_ptr = &buf[cursor];
        bool is_critical = (raw_tag & TAG_CRITICAL_FLAG) != 0;
        uint8_t clean_tag = raw_tag & (uint8_t)(~TAG_CRITICAL_FLAG);

        switch (clean_tag) {
            case TAG_NODE_ID:
                if (tag_len != 4) return PARSE_ERR_TAG_VALUE_MALFORMED;
                out_msg->node_id = read_u32_le(val_ptr);
                out_msg->present_mask |= FIELD_FLAG_NODE_ID;
                break;

            case TAG_TEMPERATURE:
                if (tag_len != 4) return PARSE_ERR_TAG_VALUE_MALFORMED;
                out_msg->temperature_mc = read_i32_le(val_ptr);
                out_msg->present_mask |= FIELD_FLAG_TEMPERATURE;
                break;

            case TAG_HUMIDITY:
                if (tag_len != 2) return PARSE_ERR_TAG_VALUE_MALFORMED;
                out_msg->humidity_cpercent = read_u16_le(val_ptr);
                out_msg->present_mask |= FIELD_FLAG_HUMIDITY;
                break;

            case TAG_VOLTAGE:
                if (tag_len != 2) return PARSE_ERR_TAG_VALUE_MALFORMED;
                out_msg->battery_mv = read_u16_le(val_ptr);
                out_msg->present_mask |= FIELD_FLAG_VOLTAGE;
                break;

            case TAG_SOIL_EC:
                if (tag_len != 2) return PARSE_ERR_TAG_VALUE_MALFORMED;
                out_msg->soil_ec_us_cm = read_u16_le(val_ptr);
                out_msg->present_mask |= FIELD_FLAG_SOIL_EC;
                break;

            case TAG_GPS_POS:
                if (tag_len != 8) return PARSE_ERR_TAG_VALUE_MALFORMED;
                out_msg->gps_latitude = read_i32_le(val_ptr);
                out_msg->gps_longitude = read_i32_le(val_ptr + 4);
                out_msg->present_mask |= FIELD_FLAG_GPS;
                break;

            default:
                // Невідомий тег: перевірка прапорця критичності
                if (is_critical) {
                    return PARSE_ERR_UNKNOWN_CRITICAL_TAG;
                }
                // Безпечний пропуск опційного поля без помилки
                out_msg->unknown_tags_skipped++;
                break;
        }

        // Пересуваємо курсор на довжину значення поля
        cursor += tag_len;
    }

    // 7. Перевірка наявності обов'язкового поля ідентифікатора станції
    if (!(out_msg->present_mask & FIELD_FLAG_NODE_ID)) {
        return PARSE_ERR_MANDATORY_FIELD_MISSING;
    }

    return PARSE_OK;
}
