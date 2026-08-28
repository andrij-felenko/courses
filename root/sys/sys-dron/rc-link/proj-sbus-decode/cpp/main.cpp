#include <stdint.h>

struct SbusData {
    uint16_t ch[16];   // 16 каналів, сирі значення 192..1792
    bool failsafe;     // приймач у failsafe — каналам не вірити
    bool frame_lost;   // цей кадр прийнято з помилкою
};

// Розпарсити 25-байтовий кадр SBUS. Повертає false, якщо рамка кадру не та.
bool sbus_parse(const uint8_t frame[25], SbusData* out) {
    if (frame[0] != 0x0F || frame[24] != 0x00)
        return false;                       // не наш кадр / зсув по байтах

    uint32_t bits = 0;                      // акумулятор бітів
    int nbits = 0;                          // скільки бітів у ньому зараз
    int ch = 0;                             // який канал заповнюємо

    for (int i = 1; i <= 22 && ch < 16; i++) {
        bits |= (uint32_t)frame[i] << nbits;   // досипати байт молодшими вперед
        nbits += 8;
        while (nbits >= 11 && ch < 16) {       // назбиралося на канал?
            out->ch[ch++] = bits & 0x07FF;     // зняти молодші 11 бітів
            bits >>= 11;
            nbits -= 11;
        }
    }

    out->frame_lost = frame[23] & 0x04;     // біт 2 байта прапорців
    out->failsafe   = frame[23] & 0x08;     // біт 3
    return true;
}
