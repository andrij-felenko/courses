#include <stdint.h>
#include <stddef.h>

#define FRAME_START 0x7E          // маркер початку кадру

// проста контрольна сума-XOR для наочності (у бойовому коді — CRC-16, див. лінк)
static uint8_t checksum(const uint8_t *p, size_t n) {
    uint8_t s = 0;
    for (size_t i = 0; i < n; i++) s ^= p[i];
    return s;
}

// зібрати кадр у buf; повертає його повну довжину в байтах
size_t pack_telemetry(uint8_t *buf, int16_t temp_c100, uint8_t status) {
    size_t i = 0;
    buf[i++] = FRAME_START;                         // [0] маркер
    buf[i++] = 3;                                    // [1] довжина корисних даних (temp2 + status1)
    buf[i++] = (uint8_t)((temp_c100 >> 8) & 0xFF);   // [2] температура, старший байт (big-endian)
    buf[i++] = (uint8_t)( temp_c100       & 0xFF);   // [3] температура, молодший байт
    buf[i++] = status;                               // [4] статус
    buf[i]   = checksum(&buf[2], 3);                 // [5] сума по полях корисних даних
    return i + 1;                                    // разом 6 байтів
}
