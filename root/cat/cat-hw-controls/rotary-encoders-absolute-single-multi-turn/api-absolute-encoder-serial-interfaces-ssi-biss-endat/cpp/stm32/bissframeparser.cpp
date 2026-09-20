// Приклад класу обробки кадру BiSS-C із перевіркою CRC6 на C++
#include <cstdint>

class BiSSFrameParser {
public:
    static bool validate_crc6(uint64_t data_word, uint8_t frame_bits, uint8_t received_crc) {
        uint8_t crc = 0x00; // Початковий зсувний регістр
        for (int i = frame_bits - 1; i >= 0; --i) {
            uint8_t bit = (data_word >> i) & 0x01;
            uint8_t crc_msb = (crc >> 5) & 0x01;
            crc <<= 1;
            if (bit ^ crc_msb) {
                crc ^= 0x03; // Поліном x^6 + x^1 + 1 (маска 0x03 для молодших бітів)
            }
        }
        return (crc & 0x3F) == (received_crc & 0x3F);
    }
};
