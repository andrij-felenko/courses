#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t magic;
    uint8_t segment_count;
    uint8_t flash_mode;
    uint8_t flash_size_freq;
    uint32_t entry_point;
} __attribute__((packed)) esp_image_header_v1_t;

typedef struct {
    uint32_t load_addr;
    uint32_t data_len;
} __attribute__((packed)) esp_image_segment_header_t;

bool validate_image_header_v1(const uint8_t *buffer, uint32_t length) {
    if (length < sizeof(esp_image_header_v1_t)) {
        return false;
    }
    const esp_image_header_v1_t *hdr = (const esp_image_header_v1_t *)buffer;
    if (hdr->magic != 0xE9) {
        return false;
    }
    uint8_t checksum = 0xEF;
    uint32_t offset = sizeof(esp_image_header_v1_t);

    for (uint8_t i = 0; i < hdr->segment_count; i++) {
        if (offset + sizeof(esp_image_segment_header_t) > length) {
            return false;
        }
        const esp_image_segment_header_t *seg = (const esp_image_segment_header_t *)(buffer + offset);
        offset += sizeof(esp_image_segment_header_t);

        if (offset + seg->data_len > length) {
            return false;
        }
        for (uint32_t j = 0; j < seg->data_len; j++) {
            checksum ^= buffer[offset + j];
        }
        offset += seg->data_len;
    }
    return true;
}
