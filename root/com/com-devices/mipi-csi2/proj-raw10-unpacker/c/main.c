#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CSI2_DT_RAW10 0x2B
#define CRC16_CCITT_POLY 0x1021

typedef enum {
    CSI2_OK = 0,
    CSI2_ERR_NULL_PTR = -1,
    CSI2_ERR_BUFFER_TOO_SMALL = -2,
    CSI2_ERR_INVALID_DATA_TYPE = -3,
    CSI2_ERR_ECC_UNCORRECTABLE = -4,
    CSI2_ERR_CRC_MISMATCH = -5
} csi2_status_t;

typedef struct {
    uint8_t virtual_channel;
    uint8_t data_type;
    uint16_t word_count;
    bool ecc_corrected;
} csi2_header_t;

// Розрахунок 6 бітів паритету Хеммінга для 24-бітного заголовка
static uint8_t csi2_calc_ecc(uint32_t data24) {
    uint8_t p0 = 0, p1 = 0, p2 = 0, p3 = 0, p4 = 0, p5 = 0;
    
    #define BIT(n) ((data24 >> (n)) & 1U)
    p0 = BIT(0)^BIT(1)^BIT(2)^BIT(4)^BIT(5)^BIT(7)^BIT(8)^BIT(10)^BIT(11)^BIT(13)^BIT(14)^BIT(16)^BIT(20)^BIT(21)^BIT(23);
    p1 = BIT(0)^BIT(1)^BIT(3)^BIT(4)^BIT(6)^BIT(7)^BIT(9)^BIT(10)^BIT(12)^BIT(13)^BIT(15)^BIT(17)^BIT(20)^BIT(22)^BIT(23);
    p2 = BIT(0)^BIT(2)^BIT(3)^BIT(5)^BIT(6)^BIT(7)^BIT(11)^BIT(12)^BIT(13)^BIT(18)^BIT(19)^BIT(20)^BIT(22)^BIT(23);
    p3 = BIT(1)^BIT(2)^BIT(3)^BIT(8)^BIT(9)^BIT(10)^BIT(11)^BIT(12)^BIT(13)^BIT(14)^BIT(15)^BIT(18)^BIT(19)^BIT(21)^BIT(22)^BIT(23);
    p4 = BIT(4)^BIT(5)^BIT(6)^BIT(7)^BIT(8)^BIT(9)^BIT(10)^BIT(11)^BIT(12)^BIT(13)^BIT(14)^BIT(15)^BIT(16)^BIT(17)^BIT(21)^BIT(22)^BIT(23);
    p5 = BIT(16)^BIT(17)^BIT(18)^BIT(19)^BIT(20)^BIT(21)^BIT(22)^BIT(23);
    #undef BIT

    return (uint8_t)(p0 | (p1 << 1) | (p2 << 2) | (p3 << 3) | (p4 << 4) | (p5 << 5));
}

// Перевірка та відновлення заголовка пакета
static csi2_status_t csi2_parse_header(const uint8_t *raw_header, csi2_header_t *out_hdr) {
    uint32_t data24 = (uint32_t)raw_header[0] |
                      ((uint32_t)raw_header[1] << 8) |
                      ((uint32_t)raw_header[2] << 16);
    uint8_t rx_ecc = raw_header[3] & 0x3F;
    uint8_t calc_ecc = csi2_calc_ecc(data24);
    uint8_t syndrome = rx_ecc ^ calc_ecc;

    out_hdr->ecc_corrected = false;

    if (syndrome != 0) {
        // Таблиця відповідності синдрому до номеру пошкодженого біта (0..23)
        static const uint8_t syndrome_table[64] = {
            [0x07] = 0,  [0x0B] = 1,  [0x0D] = 2,  [0x0E] = 3,
            [0x13] = 4,  [0x15] = 5,  [0x16] = 6,  [0x19] = 7,
            [0x1A] = 8,  [0x1C] = 9,  [0x23] = 10, [0x25] = 11,
            [0x26] = 12, [0x29] = 13, [0x2A] = 14, [0x2C] = 15,
            [0x31] = 16, [0x32] = 17, [0x34] = 18, [0x38] = 19,
            [0x1F] = 20, [0x2F] = 21, [0x37] = 22, [0x3B] = 23
        };

        if (syndrome <= 0x3F && (syndrome == 0x01 || syndrome == 0x02 || syndrome == 0x04 ||
                                 syndrome == 0x08 || syndrome == 0x10 || syndrome == 0x20)) {
            // Помилка в самому біті ECC — дані заголовка не ушкоджені
            out_hdr->ecc_corrected = true;
        } else if (syndrome <= 0x3F && syndrome_table[syndrome] != 0) {
            uint8_t bit_idx = syndrome_table[syndrome];
            data24 ^= (1U << bit_idx); // Інверсія пошкодженого біта
            out_hdr->ecc_corrected = true;
        } else {
            return CSI2_ERR_ECC_UNCORRECTABLE;
        }
    }

    out_hdr->data_type = (uint8_t)(data24 & 0x3F);
    out_hdr->virtual_channel = (uint8_t)((data24 >> 6) & 0x03);
    out_hdr->word_count = (uint16_t)((data24 >> 8) & 0xFFFF);
    return CSI2_OK;
}

// Розрахунок контрольної суми CRC-16-CCITT над байтами Payload
static uint16_t csi2_calc_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int b = 0; b < 8; b++) {
            if (crc & 0x8000) {
                crc = (uint16_t)((crc << 1) ^ CRC16_CCITT_POLY);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

// Розпакування 5-байтних блоків RAW10 у 4 пікселі uint16_t
csi2_status_t csi2_unpack_raw10_packet(
    const uint8_t *packet_buf,
    size_t packet_size,
    uint16_t *out_pixels,
    size_t max_pixels,
    size_t *actual_pixels
) {
    if (!packet_buf || !out_pixels || !actual_pixels) return CSI2_ERR_NULL_PTR;
    if (packet_size < 6) return CSI2_ERR_BUFFER_TOO_SMALL;

    csi2_header_t hdr;
    csi2_status_t status = csi2_parse_header(packet_buf, &hdr);
    if (status != CSI2_OK) return status;

    if (hdr.data_type != CSI2_DT_RAW10) return CSI2_ERR_INVALID_DATA_TYPE;

    size_t expected_total_size = 4 + (size_t)hdr.word_count + 2;
    if (packet_size < expected_total_size) return CSI2_ERR_BUFFER_TOO_SMALL;

    const uint8_t *payload = packet_buf + 4;
    uint16_t rx_crc = (uint16_t)payload[hdr.word_count] |
                      ((uint16_t)payload[hdr.word_count + 1] << 8);
    uint16_t calc_crc = csi2_calc_crc16(payload, hdr.word_count);

    if (rx_crc != calc_crc) return CSI2_ERR_CRC_MISMATCH;

    size_t num_blocks = hdr.word_count / 5;
    size_t total_pixels = num_blocks * 4;
    if (total_pixels > max_pixels) total_pixels = max_pixels;

    size_t px_idx = 0;
    for (size_t i = 0; i < num_blocks && (px_idx + 3) < max_pixels; i++) {
        const uint8_t *b = payload + (i * 5);
        uint8_t lsb_byte = b[4];

        out_pixels[px_idx + 0] = (uint16_t)(((uint16_t)b[0] << 2) | ((lsb_byte >> 0) & 0x03));
        out_pixels[px_idx + 1] = (uint16_t)(((uint16_t)b[1] << 2) | ((lsb_byte >> 2) & 0x03));
        out_pixels[px_idx + 2] = (uint16_t)(((uint16_t)b[2] << 2) | ((lsb_byte >> 4) & 0x03));
        out_pixels[px_idx + 3] = (uint16_t)(((uint16_t)b[3] << 2) | ((lsb_byte >> 6) & 0x03));
        px_idx += 4;
    }

    *actual_pixels = px_idx;
    return CSI2_OK;
}
