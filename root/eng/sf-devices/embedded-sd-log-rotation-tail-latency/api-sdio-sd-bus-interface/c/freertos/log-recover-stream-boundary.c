#include "ff.h"
#include <stdint.h>
#include <stdbool.h>

#define SCAN_SECTOR_SIZE 512U

// Пошук останнього валідного байтового зсуву всередині попередньо виділеного файла логу
uint32_t log_recover_stream_boundary(FIL *file, uint64_t *out_last_seq) {
    uint8_t sector_buf[SCAN_SECTOR_SIZE];
    UINT br = 0;
    uint32_t current_offset = 0;
    uint64_t expected_seq = 0;
    *out_last_seq = 0;

    f_lseek(file, 0);

    while (f_read(file, sector_buf, SCAN_SECTOR_SIZE, &br) == FR_OK && br == SCAN_SECTOR_SIZE) {
        bool sector_valid = true;

        for (uint32_t offset = 0; offset < SCAN_SECTOR_SIZE; offset += sizeof(sd_log_packet_t)) {
            const sd_log_packet_t *pkt = (const sd_log_packet_t *)&sector_buf[offset];

            // Якщо виявлено стерту флеш-пам'ять (0xFF) або спотворене магічне число
            if (pkt->magic != LOG_PACKET_MAGIC) {
                sector_valid = false;
                break;
            }

            // Перевірка монотонності лічильника пакетів
            if (expected_seq > 0 && pkt->seq_num != expected_seq + 1) {
                sector_valid = false; // Виявлено застарілі дані попереднього кола ротації
                break;
            }

            // Перевірка цілісності контрольної суми CRC32
            uint32_t calc_crc = calculate_crc32((const uint8_t *)pkt, sizeof(sd_log_packet_t) - sizeof(uint32_t));
            if (calc_crc != pkt->crc32) {
                sector_valid = false; // Пакет пошкоджено в момент аварійного знеструмлення
                break;
            }

            expected_seq = pkt->seq_num;
            *out_last_seq = expected_seq;
            current_offset += sizeof(sd_log_packet_t);
        }

        if (!sector_valid) {
            break;
        }
    }

    f_lseek(file, current_offset);
    return current_offset;
}
