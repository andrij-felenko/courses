/* ============================================================================
   ulog_parser.c — Потоковий парсер PX4 ULog мовою C (C99/C11)
   ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_SUBSCRIPTIONS 512
#define MAX_FORMATS 256

// Опис схеми uORB топіка
typedef struct {
    char format_name[64];
    char raw_fields[512];
    uint16_t total_size;
} ulog_format_t;

// Активна підписка msg_id -> назва схеми
typedef struct {
    bool active;
    uint16_t msg_id;
    uint8_t  multi_id;
    char message_name[64];
    const ulog_format_t *format;
} ulog_subscription_t;

// Стан декодера ULog
typedef struct {
    bool header_parsed;
    uint64_t start_timestamp;
    ulog_format_t formats[MAX_FORMATS];
    uint16_t format_count;
    ulog_subscription_t subscriptions[MAX_SUBSCRIPTIONS];
    uint32_t data_messages;
    uint32_t dropouts;
} ulog_parser_t;

void ulog_parser_init(ulog_parser_t *p) {
    memset(p, 0, sizeof(ulog_parser_t));
}

// Перевірка 16-байтного магічного заголовка файлу ULog
bool ulog_parse_header(ulog_parser_t *p, const uint8_t *buf, size_t size) {
    const uint8_t expected_magic[7] = {0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35};
    if (size < 16) return false;
    
    if (memcmp(buf, expected_magic, 7) != 0) {
        printf("Помилка: недійсний заголовок сигнатури ULog!\n");
        return false;
    }
    
    memcpy(&p->start_timestamp, buf + 7, sizeof(uint64_t));
    p->header_parsed = true;
    printf("[ULOG] Файл ініціалізовано. Системний час старту: %llu мкс\n",
           (unsigned long long)p->start_timestamp);
    return true;
}

// Реєстрація форматної схеми 'F'
static void ulog_process_format(ulog_parser_t *p, const char *fmt_str, uint16_t len) {
    if (p->format_count >= MAX_FORMATS) return;
    
    ulog_format_t *fmt = &p->formats[p->format_count];
    memset(fmt, 0, sizeof(ulog_format_t));
    
    const char *colon = strchr(fmt_str, ':');
    if (!colon) return;
    
    size_t name_len = colon - fmt_str;
    if (name_len >= sizeof(fmt->format_name)) name_len = sizeof(fmt->format_name) - 1;
    strncpy(fmt->format_name, fmt_str, name_len);
    fmt->format_name[name_len] = '\0';
    
    size_t fields_len = len - (colon - fmt_str + 1);
    if (fields_len >= sizeof(fmt->raw_fields)) fields_len = sizeof(fmt->raw_fields) - 1;
    strncpy(fmt->raw_fields, colon + 1, fields_len);
    fmt->raw_fields[fields_len] = '\0';
    
    p->format_count++;
    printf("[ULOG-F] Формат: %s -> Поля: %s\n", fmt->format_name, fmt->raw_fields);
}

// Обробка реєстрації підписки 'A'
static void ulog_process_add_msg(ulog_parser_t *p, const uint8_t *payload, uint16_t len) {
    if (len < 3) return;
    
    uint8_t multi_id = payload[0];
    uint16_t msg_id = (uint16_t)payload[1] | ((uint16_t)payload[2] << 8);
    
    if (msg_id >= MAX_SUBSCRIPTIONS) return;
    
    ulog_subscription_t *sub = &p->subscriptions[msg_id];
    sub->active = true;
    sub->msg_id = msg_id;
    sub->multi_id = multi_id;
    
    size_t name_len = len - 3;
    if (name_len >= sizeof(sub->message_name)) name_len = sizeof(sub->message_name) - 1;
    memcpy(sub->message_name, payload + 3, name_len);
    sub->message_name[name_len] = '\0';
    
    // Пошук раніше оголошеного формату
    for (int i = 0; i < p->format_count; ++i) {
        if (strcmp(p->formats[i].format_name, sub->message_name) == 0) {
            sub->format = &p->formats[i];
            break;
        }
    }
    
    printf("[ULOG-A] Підписка: ID=%u -> Топік %s (екземпляр %u)\n",
           msg_id, sub->message_name, multi_id);
}

// Потоковий розбір блоків ULog
void ulog_parse_stream(ulog_parser_t *p, const uint8_t *data, size_t size) {
    size_t offset = 0;
    
    if (!p->header_parsed) {
        if (!ulog_parse_header(p, data, size)) return;
        offset = 16;
    }
    
    while (offset + 3 <= size) {
        uint16_t msg_size = (uint16_t)data[offset] | ((uint16_t)data[offset + 1] << 8);
        uint8_t  msg_type = data[offset + 2];
        
        if (offset + 3 + msg_size > size) break; // неповний блок
        
        const uint8_t *payload = &data[offset + 3];
        
        switch (msg_type) {
            case 'F': {
                char temp[512];
                size_t cpy = (msg_size < sizeof(temp) - 1) ? msg_size : sizeof(temp) - 1;
                memcpy(temp, payload, cpy);
                temp[cpy] = '\0';
                ulog_process_format(p, temp, msg_size);
                break;
            }
            case 'A':
                ulog_process_add_msg(p, payload, msg_size);
                break;
            case 'D': {
                if (msg_size >= 2) {
                    uint16_t msg_id = (uint16_t)payload[0] | ((uint16_t)payload[1] << 8);
                    p->data_messages++;
                    if (msg_id < MAX_SUBSCRIPTIONS && p->subscriptions[msg_id].active) {
                        // Тут сирі байти передаються декодеру конкретної структури uORB
                    }
                }
                break;
            }
            case 'L': {
                if (msg_size >= 9) {
                    uint8_t level = payload[0];
                    uint64_t ts;
                    memcpy(&ts, payload + 1, sizeof(uint64_t));
                    char text_buf[256];
                    size_t tlen = msg_size - 9;
                    if (tlen >= sizeof(text_buf)) tlen = sizeof(text_buf) - 1;
                    memcpy(text_buf, payload + 9, tlen);
                    text_buf[tlen] = '\0';
                    printf("  [LOG L%u] t=%llu us: %s\n", level, (unsigned long long)ts, text_buf);
                }
                break;
            }
            case 'S': {
                if (msg_size >= 2) {
                    uint16_t dur = (uint16_t)payload[0] | ((uint16_t)payload[1] << 8);
                    p->dropouts++;
                    printf("  [DROPOUT] Втрата даних тривалістю: %u мс\n", dur);
                }
                break;
            }
            default:
                break;
        }
        
        offset += 3 + msg_size;
    }
}
