#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

/* Перелік відомих тегів протоколу */
typedef enum {
    TLV_TAG_VOLTAGE_MV     = 0x01,
    TLV_TAG_CURRENT_MA     = 0x02,
    TLV_TAG_TEMPERATURE    = 0x03,
    TLV_TAG_DEVICE_NAME    = 0x04,
    TLV_TAG_NETWORK_CONFIG = 0x05,
    /* Підтеги для вкладеного контейнера TLV_TAG_NETWORK_CONFIG */
    TLV_SUBTAG_IP_ADDR     = 0x10,
    TLV_SUBTAG_PORT        = 0x11
} TlvTag_t;

/* Коди результату обробки */
typedef enum {
    TLV_OK = 0,
    TLV_ERR_BUFFER_OVERRUN = -1,
    TLV_ERR_INVALID_LENGTH = -2,
    TLV_ERR_NESTED_INVALID = -3
} TlvStatus_t;

/* Структура одного розібраного TLV елемента */
typedef struct {
    uint8_t tag;
    uint8_t length;
    const uint8_t *value;
} TlvElement_t;

/* Структура мережевих налаштувань */
typedef struct {
    uint32_t ip_address; /* IPv4 у мережевому порядку */
    uint16_t port;
    bool     has_ip;
    bool     has_port;
} NetworkConfig_t;

/* Цільова бізнес-структура з дефолтами та прапорцями наявності */
typedef struct {
    uint16_t voltage_mv;
    int32_t  current_ma;
    int16_t  temperature_c_x100;
    char     device_name[33];
    NetworkConfig_t net_cfg;
    
    /* Бітова маска наявності полів у прийнятому пакеті */
    struct {
        uint8_t has_voltage : 1;
        uint8_t has_current : 1;
        uint8_t has_temperature : 1;
        uint8_t has_device_name : 1;
        uint8_t has_net_config : 1;
    } flags;
    
    /* Лічильник пропущених невідомих тегів */
    uint16_t unknown_tags_count;
} TelemetryData_t;

/* 
 * Низькорівневий ітератор потоку: зчитує один TLV-елемент.
 * Зсуває *cursor на наступний елемент.
 * Повертає true, якщо елемент успішно прочитано, false якщо потік закінчився або пошкоджений.
 */
static bool tlv_next_element(const uint8_t *buffer, size_t total_len, 
                             size_t *cursor, TlvElement_t *out_elem) 
{
    if (cursor == NULL || out_elem == NULL || buffer == NULL) {
        return false;
    }
    
    /* Чи залишилося хоча б 2 байти на заголовок (Tag + Length)? */
    if (*cursor + 2 > total_len) {
        return false;
    }
    
    uint8_t tag = buffer[*cursor];
    uint8_t len = buffer[*cursor + 1];
    
    /* Безпечна перевірка без ризику цілочисельного переповнення */
    if (len > (total_len - *cursor - 2)) {
        return false;
    }
    
    out_elem->tag = tag;
    out_elem->length = len;
    out_elem->value = &buffer[*cursor + 2];
    
    /* Переміщуємо курсор на наступний TLV-блок (заголовок 2 байти + тіло) */
    *cursor += 2 + len;
    return true;
}

/* 
 * Розбір вкладеного контейнера налаштувань мережі (Nested TLV).
 */
static TlvStatus_t parse_nested_network_config(const uint8_t *buffer, size_t len, 
                                               NetworkConfig_t *out_net) 
{
    size_t cursor = 0;
    TlvElement_t elem;
    
    out_net->ip_address = 0;
    out_net->port = 0;
    out_net->has_ip = false;
    out_net->has_port = false;
    
    while (cursor < len) {
        if (!tlv_next_element(buffer, len, &cursor, &elem)) {
            return TLV_ERR_NESTED_INVALID;
        }
        
        switch (elem.tag) {
            case TLV_SUBTAG_IP_ADDR:
                if (elem.length == sizeof(uint32_t)) {
                    uint32_t ip = (uint32_t)elem.value[0] |
                                  ((uint32_t)elem.value[1] << 8) |
                                  ((uint32_t)elem.value[2] << 16) |
                                  ((uint32_t)elem.value[3] << 24);
                    out_net->ip_address = ip;
                    out_net->has_ip = true;
                }
                break;
                
            case TLV_SUBTAG_PORT:
                if (elem.length == sizeof(uint16_t)) {
                    uint16_t port = (uint16_t)(elem.value[0] | (elem.value[1] << 8));
                    out_net->port = port;
                    out_net->has_port = true;
                }
                break;
                
            default:
                /* Невідомий підтег налаштувань безпечно ігноруємо */
                break;
        }
    }
    
    return TLV_OK;
}

/* 
 * Ініціалізація структури дефолтними значеннями перед розбором.
 */
void telemetry_data_init_defaults(TelemetryData_t *data) {
    if (data == NULL) return;
    
    memset(data, 0, sizeof(TelemetryData_t));
    data->voltage_mv = 0;
    data->current_ma = 0;
    data->temperature_c_x100 = -32768; /* Маркер відсутності даних */
    data->device_name[0] = '\0';
    data->unknown_tags_count = 0;
}

/* 
 * Високорівневий розбір усього TLV-пакета в структуру даних.
 */
TlvStatus_t telemetry_parse_tlv_stream(const uint8_t *buffer, size_t total_len, 
                                       TelemetryData_t *out_data) 
{
    if (buffer == NULL || out_data == NULL) {
        return TLV_ERR_BUFFER_OVERRUN;
    }
    
    telemetry_data_init_defaults(out_data);
    
    size_t cursor = 0;
    TlvElement_t elem;
    
    while (cursor < total_len) {
        if (!tlv_next_element(buffer, total_len, &cursor, &elem)) {
            /* Потік містить обрізаний або некоректний заголовок */
            return TLV_ERR_INVALID_LENGTH;
        }
        
        switch (elem.tag) {
            case TLV_TAG_VOLTAGE_MV:
                if (elem.length == sizeof(uint16_t)) {
                    /* Безпечне декодування little-endian без порушення вирівнювання */
                    out_data->voltage_mv = (uint16_t)(elem.value[0] | (elem.value[1] << 8));
                    out_data->flags.has_voltage = 1;
                }
                break;
                
            case TLV_TAG_CURRENT_MA:
                if (elem.length == sizeof(int32_t)) {
                    uint32_t raw = (uint32_t)elem.value[0] |
                                   ((uint32_t)elem.value[1] << 8) |
                                   ((uint32_t)elem.value[2] << 16) |
                                   ((uint32_t)elem.value[3] << 24);
                    out_data->current_ma = (int32_t)raw;
                    out_data->flags.has_current = 1;
                }
                break;
                
            case TLV_TAG_TEMPERATURE:
                if (elem.length == sizeof(int16_t)) {
                    uint16_t raw = (uint16_t)(elem.value[0] | (elem.value[1] << 8));
                    out_data->temperature_c_x100 = (int16_t)raw;
                    out_data->flags.has_temperature = 1;
                }
                break;
                
            case TLV_TAG_DEVICE_NAME:
                if (elem.length > 0 && elem.length < sizeof(out_data->device_name)) {
                    memcpy(out_data->device_name, elem.value, elem.length);
                    out_data->device_name[elem.length] = '\0';
                    out_data->flags.has_device_name = 1;
                }
                break;
                
            case TLV_TAG_NETWORK_CONFIG:
                if (parse_nested_network_config(elem.value, elem.length, &out_data->net_cfg) == TLV_OK) {
                    out_data->flags.has_net_config = 1;
                }
                break;
                
            default:
                /* 
                 * ПРЯМА СУМІСНІСТЬ (Forward Compatibility):
                 * Невідомий тег просто ігнорується, курсор уже зсунуто вперед на elem.length.
                 */
                out_data->unknown_tags_count++;
                break;
        }
    }
    
    return TLV_OK;
}
