#include "ff.h"
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define LOG_FRAME_MAGIC     0xA55A
#define CHUNK_SCAN_SIZE     512

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint16_t payload_len;
    uint32_t seq_id;
    uint32_t timestamp_ms;
} frame_header_t;
#pragma pack(pop)

// Програмний розрахунок CRC32 для валідації цілісності
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

// Сканування пре-алокованого файлу для виявлення точки збою живлення
FRESULT log_recover_valid_boundary(FIL *file, uint32_t *valid_bytes_out) {
    FRESULT fr = f_lseek(file, 0);
    if (fr != FR_OK) return fr;

    uint8_t sector_buf[CHUNK_SCAN_SIZE];
    UINT br = 0;
    uint32_t current_file_pos = 0;

    for (;;) {
        fr = f_read(file, sector_buf, CHUNK_SCAN_SIZE, &br);
        if (fr != FR_OK || br < sizeof(frame_header_t)) break;

        size_t offset = 0;
        bool frame_valid = true;

        while (offset + sizeof(frame_header_t) + sizeof(uint32_t) <= br) {
            frame_header_t *hdr = (frame_header_t *)&sector_buf[offset];
            if (hdr->magic != LOG_FRAME_MAGIC) {
                frame_valid = false;
                break;
            }

            size_t total_frame_len = sizeof(frame_header_t) + hdr->payload_len + sizeof(uint32_t);
            if (offset + total_frame_len > br) break;

            uint32_t stored_crc;
            memcpy(&stored_crc, &sector_buf[offset + sizeof(frame_header_t) + hdr->payload_len], sizeof(uint32_t));
            uint32_t computed_crc = calculate_crc32(&sector_buf[offset], sizeof(frame_header_t) + hdr->payload_len);

            if (stored_crc != computed_crc) {
                frame_valid = false;
                break;
            }

            offset += total_frame_len;
            current_file_pos += total_frame_len;
        }

        if (!frame_valid || br < CHUNK_SCAN_SIZE) break;
    }

    *valid_bytes_out = current_file_pos;
    return f_lseek(file, current_file_pos);
}

// Замір хвостової затримки запису сектора через апаратні цикли ядра
uint32_t measure_write_latency_cycles(FIL *file, const void *buf, UINT size) {
    // Увімкнення лічильника DWT (якщо не активовано)
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    uint32_t start_cycles = DWT->CYCCNT;
    UINT bw = 0;
    f_write(file, buf, size, &bw);
    uint32_t end_cycles = DWT->CYCCNT;

    return (end_cycles >= start_cycles) ? (end_cycles - start_cycles) : (UINT32_MAX - start_cycles + end_cycles);
}
