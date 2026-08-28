#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FRAME_MAGIC 0x4850
#define HEADER_SIZE 8
#define TRAILER_SIZE 4

typedef struct {
    uint16_t magic;
    uint8_t  version;
    uint8_t  flags;
    uint32_t payload_len;
} FrameHeaderC;

typedef struct {
    FrameHeaderC header;
    const uint8_t* payload_ptr;
    size_t payload_len;
    uint32_t crc32;
} ParsedFrameC;

// Допоміжна функція перетворення endianness (network to host)
static uint32_t ntohl_custom(uint32_t val) {
    return ((val & 0xFF000000) >> 24) |
           ((val & 0x00FF0000) >> 8)  |
           ((val & 0x0000FF00) << 8)  |
           ((val & 0x000000FF) << 24);
}

static uint16_t ntohs_custom(uint16_t val) {
    return (uint16_t)((val >> 8) | (val << 8));
}

// Парсер у стилі C: вимагає сирого вказівника та розрахунку зміщень
bool parse_frame_c(const uint8_t* buffer, size_t buffer_len, ParsedFrameC* out_frame) {
    if (buffer == NULL || out_frame == NULL) {
        return false;
    }

    // 1. Перевірка мінімального розміру для заголовка та трейлера
    if (buffer_len < HEADER_SIZE + TRAILER_SIZE) {
        return false;
    }

    // 2. Безпечне зчитування заголовка через memcpy (уникнення unaligned access)
    FrameHeaderC hdr;
    memcpy(&hdr, buffer, sizeof(FrameHeaderC));
    hdr.magic = ntohs_custom(hdr.magic);
    hdr.payload_len = ntohl_custom(hdr.payload_len);

    if (hdr.magic != FRAME_MAGIC || hdr.version != 1) {
        return false;
    }

    // 3. Перевірка чи достатньо байтів у буфері для оголошеного payload_len
    size_t total_expected = HEADER_SIZE + hdr.payload_len + TRAILER_SIZE;
    if (buffer_len < total_expected) {
        return false;
    }

    // 4. Виділення вказівника на payload упевнившись у межах
    out_frame->header = hdr;
    out_frame->payload_ptr = buffer + HEADER_SIZE;
    out_frame->payload_len = hdr.payload_len;

    // 5. Зчитування контрольної суми
    const uint8_t* trailer_ptr = buffer + HEADER_SIZE + hdr.payload_len;
    uint32_t raw_crc;
    memcpy(&raw_crc, trailer_ptr, sizeof(uint32_t));
    out_frame->crc32 = ntohl_custom(raw_crc);

    return true;
}
