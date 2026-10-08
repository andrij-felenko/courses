#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Результат діагностики кадру JPEG
typedef enum {
    JPEG_VALID = 0,
    JPEG_ERR_NO_SOI,
    JPEG_ERR_NO_EOI,
    JPEG_ERR_BUFFER_OVERFLOW,
    JPEG_ERR_CORRUPTED_MARKER
} jpeg_status_t;

// Перевірка цілісності захопленого в SRAM буфера JPEG
jpeg_status_t ov3640_validate_jpeg_buffer(const uint8_t *buf, size_t rx_bytes, size_t *actual_jpeg_size) {
    if (rx_bytes < 4) {
        return JPEG_ERR_BUFFER_OVERFLOW;
    }

    // Перевірка маркеру SOI (0xFFD8)
    if (buf[0] != 0xFF || buf[1] != 0xD8) {
        return JPEG_ERR_NO_SOI;
    }

    // Пошук маркеру EOI (0xFFD9) з урахуванням byte stuffing (0xFF00)
    bool eoi_found = false;
    size_t eoi_index = 0;

    for (size_t i = 2; i < rx_bytes - 1; i++) {
        if (buf[i] == 0xFF) {
            uint8_t next_byte = buf[i + 1];
            if (next_byte == 0xD9) { // Маркер EOI
                eoi_found = true;
                eoi_index = i + 2;
                break;
            } else if (next_byte == 0x00) {
                // Пропуск вставленого байта byte stuffing
                i++;
            }
        }
    }

    if (!eoi_found) {
        return JPEG_ERR_NO_EOI;
    }

    *actual_jpeg_size = eoi_index;
    return JPEG_VALID;
}
