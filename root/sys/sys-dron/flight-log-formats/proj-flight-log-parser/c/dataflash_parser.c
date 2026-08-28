/* ============================================================================
   dataflash_parser.c — Потоковий парсер ArduPilot DataFlash мовою C (C99/C11)
   ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DF_HEAD1 0xA3
#define DF_HEAD2 0x95
#define DF_MSG_FMT 0x80
#define MAX_DF_TYPES 256

// Структура дескриптора схеми повідомлення DataFlash
typedef struct {
    bool     valid;
    uint8_t  type_id;
    uint8_t  length;
    char     name[5];       // 4 символи назви + нуль-термінатор
    char     format[17];    // до 16 символьних специфікаторів типів
    char     columns[65];   // назви стовпчиків через кому
} df_message_format_t;

// Стан потокового парсера
typedef struct {
    df_message_format_t formats[MAX_DF_TYPES];
    uint32_t parsed_messages;
    uint32_t fmt_messages;
    uint32_t sync_errors;
} df_parser_t;

// Ініціалізація стану парсера
void df_parser_init(df_parser_t *p) {
    memset(p, 0, sizeof(df_parser_t));
}

// Безпечне зчитування цілих та дробових чисел без невирівняного доступу (Little-Endian)
static inline uint16_t read_u16_le(const uint8_t *buf) {
    return (uint16_t)buf[0] | ((uint16_t)buf[1] << 8);
}

static inline int16_t read_i16_le(const uint8_t *buf) {
    return (int16_t)read_u16_le(buf);
}

static inline uint32_t read_u32_le(const uint8_t *buf) {
    return (uint32_t)buf[0] | ((uint32_t)buf[1] << 8) |
           ((uint32_t)buf[2] << 16) | ((uint32_t)buf[3] << 24);
}

static inline int32_t read_i32_le(const uint8_t *buf) {
    return (int32_t)read_u32_le(buf);
}

static inline uint64_t read_u64_le(const uint8_t *buf) {
    uint64_t low = read_u32_le(buf);
    uint64_t high = read_u32_le(buf + 4);
    return low | (high << 32);
}

static inline float read_float_le(const uint8_t *buf) {
    uint32_t u = read_u32_le(buf);
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

// Реєстрація схеми нового типу повідомлення з пакету FMT (довжина 86 байтів payload)
static void process_fmt_payload(df_parser_t *p, const uint8_t *payload) {
    uint8_t type = payload[0];
    uint8_t len  = payload[1];
    
    df_message_format_t *fmt = &p->formats[type];
    fmt->valid = true;
    fmt->type_id = type;
    fmt->length = len;
    
    memcpy(fmt->name, payload + 2, 4);
    fmt->name[4] = '\0';
    
    memcpy(fmt->format, payload + 6, 16);
    fmt->format[16] = '\0';
    
    memcpy(fmt->columns, payload + 22, 64);
    fmt->columns[64] = '\0';
    
    p->fmt_messages++;
    printf("[FMT] ID: 0x%02X (%3u), Name: %-4s, Len: %2u, Format: %s\n",
           type, type, fmt->name, len, fmt->format);
}

// Декодування корисного навантаження зареєстрованого повідомлення даних
static void process_data_payload(df_parser_t *p, uint8_t type, const uint8_t *payload) {
    const df_message_format_t *fmt = &p->formats[type];
    p->parsed_messages++;
    
    // Обробка касетного повідомлення просторової орієнтації ATT (Attitude)
    if (strcmp(fmt->name, "ATT") == 0 && strcmp(fmt->format, "Qcccc") == 0) {
        uint64_t time_us   = read_u64_le(payload);
        float des_roll    = read_i16_le(payload + 8) / 100.0f;
        float roll        = read_i16_le(payload + 10) / 100.0f;
        float des_pitch   = read_i16_le(payload + 12) / 100.0f;
        float pitch       = read_i16_le(payload + 14) / 100.0f;
        printf("  [ATT] t=%llu us: Roll=%.2f deg (Des=%.2f), Pitch=%.2f deg (Des=%.2f)\n",
               (unsigned long long)time_us, roll, des_roll, pitch, des_pitch);
    }
    // Обробка повідомлення супутникової навігації GPS
    else if (strcmp(fmt->name, "GPS") == 0) {
        uint64_t time_us = read_u64_le(payload);
        uint8_t status   = payload[8];
        int32_t lat_raw  = read_i32_le(payload + 16);
        int32_t lng_raw  = read_i32_le(payload + 20);
        float alt        = read_float_le(payload + 24);
        printf("  [GPS] t=%llu us: Fix=%u, Lat=%.7f, Lng=%.7f, Alt=%.2f m\n",
               (unsigned long long)time_us, status, lat_raw / 1e7, lng_raw / 1e7, alt);
    }
}

// Головна функція потокового розбору буфера довільного розміру
void df_parse_stream(df_parser_t *p, const uint8_t *data, size_t size) {
    size_t offset = 0;
    
    while (offset + 3 <= size) {
        // Пошук синхронізуючого маркера 0xA3 0x95
        if (data[offset] != DF_HEAD1 || data[offset + 1] != DF_HEAD2) {
            offset++;
            p->sync_errors++;
            continue;
        }
        
        uint8_t type = data[offset + 2];
        
        // Обробка повідомлення FMT (фіксована довжина 89 байтів разом з заголовком)
        if (type == DF_MSG_FMT) {
            if (offset + 89 > size) break; // неповний блок у кінці чанка
            process_fmt_payload(p, &data[offset + 3]);
            offset += 89;
            continue;
        }
        
        // Обробка відомого типу повідомлення
        const df_message_format_t *fmt = &p->formats[type];
        if (fmt->valid) {
            if (offset + fmt->length > size) break; // очікуємо наступну порцію даних
            process_data_payload(p, type, &data[offset + 3]);
            offset += fmt->length;
        } else {
            // Тип повідомлення ще не зареєстрований через FMT: зсув для ресинхронізації
            offset++;
            p->sync_errors++;
        }
    }
}
