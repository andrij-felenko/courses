#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define NDEF_TNF_WELL_KNOWN   0x01
#define NDEF_TNF_MIME_MEDIA   0x02

#define NDEF_FLAG_MB          0x80
#define NDEF_FLAG_ME          0x40
#define NDEF_FLAG_CF          0x20
#define NDEF_FLAG_SR          0x10
#define NDEF_FLAG_IL          0x08

#define BLE_AD_TYPE_FLAGS     0x01
#define BLE_AD_TYPE_NAME      0x09
#define BLE_AD_TYPE_TK        0x10
#define BLE_AD_TYPE_LE_ADDR   0x1B
#define BLE_AD_TYPE_LE_ROLE   0x1C

typedef enum {
    NDEF_OK = 0,
    NDEF_ERR_BUFFER_OVERFLOW,
    NDEF_ERR_INVALID_PARAM,
    NDEF_ERR_I2C_FAULT
} ndef_status_t;

typedef struct {
    uint8_t *buffer;
    size_t   capacity;
    size_t   length;
    size_t   record_count;
} ndef_msg_t;

void ndef_msg_init(ndef_msg_t *msg, uint8_t *storage, size_t capacity) {
    msg->buffer = storage;
    msg->capacity = capacity;
    msg->length = 0;
    msg->record_count = 0;
}

ndef_status_t ndef_add_uri(ndef_msg_t *msg, uint8_t prefix_code, const char *uri_str, bool is_last) {
    if (!msg || !uri_str) return NDEF_ERR_INVALID_PARAM;
    
    size_t uri_len = strlen(uri_str);
    size_t payload_len = 1 + uri_len; // 1 байт префіксу + рядок URI
    size_t record_overhead = 4;        // Header (1B) + TypeLen (1B) + PayloadLen (1B) + Type (1B: 'U')
    
    if (msg->length + record_overhead + payload_len > msg->capacity) {
        return NDEF_ERR_BUFFER_OVERFLOW;
    }
    
    uint8_t header = NDEF_FLAG_SR | NDEF_TNF_WELL_KNOWN;
    if (msg->record_count == 0) header |= NDEF_FLAG_MB;
    if (is_last) header |= NDEF_FLAG_ME;
    
    uint8_t *ptr = msg->buffer + msg->length;
    *ptr++ = header;
    *ptr++ = 0x01; // Type Length = 1
    *ptr++ = (uint8_t)payload_len;
    *ptr++ = 'U';  // Type = 'U' (URI)
    *ptr++ = prefix_code;
    memcpy(ptr, uri_str, uri_len);
    
    msg->length += (record_overhead + payload_len);
    msg->record_count++;
    return NDEF_OK;
}

ndef_status_t ndef_add_ble_oob(ndef_msg_t *msg, 
                              const uint8_t mac_le[6], 
                              uint8_t addr_type, 
                              const uint8_t tk[16], 
                              const char *device_name, 
                              bool is_last) {
    if (!msg || !mac_le || !tk) return NDEF_ERR_INVALID_PARAM;
    
    const char mime_type[] = "application/vnd.bluetooth.ep.oob";
    size_t mime_len = strlen(mime_type);
    size_t name_len = device_name ? strlen(device_name) : 0;
    
    // Розрахунок довжини корисного навантаження (AD Data)
    // 1. Flags: Len(1) + Type(1) + Val(1) = 3B
    // 2. LE Addr: Len(1) + Type(1) + MAC(6) + Type(1) = 9B
    // 3. LE Role: Len(1) + Type(1) + Val(1) = 3B
    // 4. TK: Len(1) + Type(1) + Key(16) = 18B
    // 5. Name (якщо є): Len(1) + Type(1) + Str(name_len) = 2 + name_len
    size_t payload_len = 3 + 9 + 3 + 18 + (name_len > 0 ? (2 + name_len) : 0);
    size_t record_overhead = 3 + mime_len; // Header (1B) + TypeLen (1B) + PayloadLen (1B) + Type(mime_len)
    
    if (msg->length + record_overhead + payload_len > msg->capacity) {
        return NDEF_ERR_BUFFER_OVERFLOW;
    }
    
    uint8_t header = NDEF_FLAG_SR | NDEF_TNF_MIME_MEDIA;
    if (msg->record_count == 0) header |= NDEF_FLAG_MB;
    if (is_last) header |= NDEF_FLAG_ME;
    
    uint8_t *ptr = msg->buffer + msg->length;
    *ptr++ = header;
    *ptr++ = (uint8_t)mime_len;
    *ptr++ = (uint8_t)payload_len;
    memcpy(ptr, mime_type, mime_len);
    ptr += mime_len;
    
    // AD Structure 1: Flags (LE General Discoverable + BR/EDR Not Supported)
    *ptr++ = 0x02; // Довжина поля (Type + Data)
    *ptr++ = BLE_AD_TYPE_FLAGS;
    *ptr++ = 0x06; // 0x02 (LE General Disc) | 0x04 (No BR/EDR)
    
    // AD Structure 2: LE Bluetooth Device Address (6 байтів MAC + 1 байт тип адреси)
    *ptr++ = 0x08;
    *ptr++ = BLE_AD_TYPE_LE_ADDR;
    memcpy(ptr, mac_le, 6);
    ptr += 6;
    *ptr++ = addr_type; // 0x00 = Public, 0x01 = Random
    
    // AD Structure 3: LE Role (0x00 = Only Peripheral)
    *ptr++ = 0x02;
    *ptr++ = BLE_AD_TYPE_LE_ROLE;
    *ptr++ = 0x00;
    
    // AD Structure 4: Security Manager TK (16 байтів)
    *ptr++ = 0x11; // 17 байтів (1 байт Type + 16 байтів TK)
    *ptr++ = BLE_AD_TYPE_TK;
    memcpy(ptr, tk, 16);
    ptr += 16;
    
    // AD Structure 5: Complete Local Name (опціонально)
    if (name_len > 0) {
        *ptr++ = (uint8_t)(1 + name_len);
        *ptr++ = BLE_AD_TYPE_NAME;
        memcpy(ptr, device_name, name_len);
        ptr += name_len;
    }
    
    msg->length += (record_overhead + payload_len);
    msg->record_count++;
    return NDEF_OK;
}
