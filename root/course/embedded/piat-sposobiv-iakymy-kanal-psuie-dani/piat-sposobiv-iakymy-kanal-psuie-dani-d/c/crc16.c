#include "crc16.h"

// Побітове ділення многочленів у GF(2): жодної таблиці на 512 байтів,
// що на дрібному мікроконтролері важить більше за кілька тактів на байт.
uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFU;

    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int bit = 0; bit < 8; ++bit) {
            // Старший біт регістра каже, чи віднімати (тобто XOR-ити) твірний поліном.
            crc = (crc & 0x8000U) ? (uint16_t)((crc << 1) ^ 0x1021U)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}
