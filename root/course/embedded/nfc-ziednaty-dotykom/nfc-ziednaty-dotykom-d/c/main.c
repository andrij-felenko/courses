#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define NDEF_TNF_WELL_KNOWN   0x01
#define NDEF_TNF_MIME_MEDIA   0x02
#define NDEF_FLAG_MB          0x80
#define NDEF_FLAG_ME          0x40
#define NDEF_FLAG_SR          0x10

typedef struct {
    uint8_t *raw_buf;
    size_t   max_size;
    size_t   offset;
    size_t   count;
} ndef_builder_t;

void ndef_init(ndef_builder_t *b, uint8_t *storage, size_t max_size) {
    b->raw_buf = storage;
    b->max_size = max_size;
    b->offset = 0;
    b->count = 0;
}

bool ndef_append_uri(ndef_builder_t *b, uint8_t prefix, const char *url, bool is_last) {
    size_t url_len = strlen(url);
    size_t payload_len = 1 + url_len;
    size_t total_record_len = 4 + payload_len; // Header + TypeLen + PayloadLen + Type('U') + Payload
    
    if (b->offset + total_record_len > b->max_size) return false;
    
    uint8_t header = NDEF_FLAG_SR | NDEF_TNF_WELL_KNOWN;
    if (b->count == 0) header |= NDEF_FLAG_MB;
    if (is_last) header |= NDEF_FLAG_ME;
    
    b->raw_buf[b->offset++] = header;
    b->raw_buf[b->offset++] = 0x01; // Type Length = 1
    b->raw_buf[b->offset++] = (uint8_t)payload_len;
    b->raw_buf[b->offset++] = 'U';  // RTD URI
    b->raw_buf[b->offset++] = prefix;
    memcpy(&b->raw_buf[b->offset], url, url_len);
    b->offset += url_len;
    
    b->count++;
    return true;
}

bool ndef_append_ble_oob(ndef_builder_t *b, const uint8_t mac[6], const uint8_t tk[16], bool is_last) {
    const char mime[] = "application/vnd.bluetooth.ep.oob";
    size_t mime_len = strlen(mime);
    // 3B (Flags) + 9B (LE MAC: Len + Type + 6B MAC + 1B Type) + 18B (TK: Len + Type + 16B Key) = 30B
    size_t payload_len = 3 + 9 + 18;
    size_t total_record_len = 3 + mime_len + payload_len;
    
    if (b->offset + total_record_len > b->max_size) return false;
    
    uint8_t header = NDEF_FLAG_SR | NDEF_TNF_MIME_MEDIA;
    if (b->count == 0) header |= NDEF_FLAG_MB;
    if (is_last) header |= NDEF_FLAG_ME;
    
    b->raw_buf[b->offset++] = header;
    b->raw_buf[b->offset++] = (uint8_t)mime_len;
    b->raw_buf[b->offset++] = (uint8_t)payload_len;
    memcpy(&b->raw_buf[b->offset], mime, mime_len);
    b->offset += mime_len;
    
    // 1. Flags AD
    b->raw_buf[b->offset++] = 0x02;
    b->raw_buf[b->offset++] = 0x01; // AD Type: Flags
    b->raw_buf[b->offset++] = 0x06; // LE General Discoverable + No BR/EDR
    
    // 2. LE Device Address AD (Little-Endian MAC + Public Addr 0x00)
    b->raw_buf[b->offset++] = 0x08;
    b->raw_buf[b->offset++] = 0x1B; // AD Type: LE Bluetooth Device Address
    memcpy(&b->raw_buf[b->offset], mac, 6);
    b->offset += 6;
    b->raw_buf[b->offset++] = 0x00; // Public Address
    
    // 3. Security Manager TK AD
    b->raw_buf[b->offset++] = 0x11;
    b->raw_buf[b->offset++] = 0x10; // AD Type: Security Manager TK
    memcpy(&b->raw_buf[b->offset], tk, 16);
    b->offset += 16;
    
    b->count++;
    return true;
}
