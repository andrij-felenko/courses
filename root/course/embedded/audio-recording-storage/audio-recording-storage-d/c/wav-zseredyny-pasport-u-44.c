#include <stdint.h>
#include <string.h>

// Кладе little-endian числа явно — не залежить від порядку байтів ядра.
static void put_u32(uint8_t *p, uint32_t v) {
    p[0] = v; p[1] = v >> 8; p[2] = v >> 16; p[3] = v >> 24;
}
static void put_u16(uint8_t *p, uint16_t v) {
    p[0] = v; p[1] = v >> 8;
}

// Заповнює 44 байти заголовка. data_bytes — розмір самого звуку в байтах.
void wav_header(uint8_t hdr[44], uint32_t sample_rate,
                uint16_t channels, uint16_t bits, uint32_t data_bytes) {
    uint16_t block_align = channels * bits / 8;
    uint32_t byte_rate   = sample_rate * block_align;

    memcpy(hdr + 0,  "RIFF", 4);
    put_u32(hdr + 4,  36 + data_bytes);   // розмір файлу мінус 8
    memcpy(hdr + 8,  "WAVE", 4);

    memcpy(hdr + 12, "fmt ", 4);
    put_u32(hdr + 16, 16);                // довжина блоку fmt
    put_u16(hdr + 20, 1);                 // PCM
    put_u16(hdr + 22, channels);
    put_u32(hdr + 24, sample_rate);
    put_u32(hdr + 28, byte_rate);
    put_u16(hdr + 32, block_align);
    put_u16(hdr + 34, bits);

    memcpy(hdr + 36, "data", 4);
    put_u32(hdr + 40, data_bytes);        // розмір самого звуку
}
