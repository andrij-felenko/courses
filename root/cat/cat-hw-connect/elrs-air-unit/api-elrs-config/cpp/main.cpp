#include <stdint.h>
#include <string.h>

// Побудова CRSF-кадру каналів на боці МК (передавач / місток на іншу шину).
#define CRSF_SYNC           0xC8   // адреса FC / байт-старт
#define CRSF_FRAMETYPE_RC   0x16   // тип: пакет 16 RC-каналів
#define CRSF_CENTER         992    // центр стіка (1500 мкс) у «тіках»

// CRC8/DVB-S2, поліном 0xD5 — той самий, що в кадрі CRSF.
static uint8_t crsf_crc8(const uint8_t *ptr, uint8_t len) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; ++i) {
        crc ^= ptr[i];
        for (uint8_t b = 0; b < 8; ++b)
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0xD5)
                               : (uint8_t)(crc << 1);
    }
    return crc;
}

// 16 каналів по 11 біт (0…2047) → 22 байти, little-endian.
static void pack_channels(const uint16_t ch[16], uint8_t out[22]) {
    uint32_t acc = 0;   // накопичувач бітів
    uint8_t  bits = 0;  // скільки валідних бітів зараз в acc
    uint8_t  o = 0;     // індекс вихідного байта
    for (uint8_t c = 0; c < 16; ++c) {
        acc |= (uint32_t)(ch[c] & 0x7FF) << bits;   // доливаємо 11 біт зверху
        bits += 11;
        while (bits >= 8) {                          // зчерпуємо готові байти знизу
            out[o++] = (uint8_t)(acc & 0xFF);
            acc >>= 8;
            bits -= 8;
        }
    }
    // 16×11 = 176 біт = рівно 22 байти, залишку немає
}

// Повний кадр каналів у buf; повертає його довжину (26 байтів).
uint8_t crsf_build_rc_frame(const uint16_t ch[16], uint8_t buf[26]) {
    uint8_t payload[22];
    pack_channels(ch, payload);
    uint8_t len = 22 + 2;               // тип(1) + дані(22) + CRC(1) = 24
    buf[0] = CRSF_SYNC;                 // старт
    buf[1] = len;                       // поле довжини
    buf[2] = CRSF_FRAMETYPE_RC;         // тип
    memcpy(&buf[3], payload, 22);       // дані
    buf[3 + 22] = crsf_crc8(&buf[2], 1 + 22);  // CRC над типом+даними
    return 2 + len;                     // повний кадр = старт+довжина+тіло = 26
}
