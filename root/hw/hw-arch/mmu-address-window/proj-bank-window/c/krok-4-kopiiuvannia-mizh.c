#include <stdint.h>
#include <stddef.h>

// Копіювати n байтів зі зсуву src_off банку src_bank
// у зсув dst_off банку dst_bank. Через проміжний буфер у RAM.
void copy_between_banks(uint8_t src_bank, uint16_t src_off,
                        uint8_t dst_bank, uint16_t dst_off,
                        size_t n) {
    uint8_t buf[64];                       // острівець у нерухомій RAM

    while (n > 0) {
        size_t chunk = (n < sizeof buf) ? n : sizeof buf;

        // Фаза читання: у вікні — джерело.
        select_bank(src_bank);
        for (size_t i = 0; i < chunk; i++)
            buf[i] = WINDOW[src_off + i];   // з банку src у буфер (у RAM)

        // Фаза запису: у вікні — приймач. Буфер у RAM перемикання пережив.
        select_bank(dst_bank);
        for (size_t i = 0; i < chunk; i++)
            WINDOW[dst_off + i] = buf[i];    // з буфера в банк dst

        src_off += chunk;
        dst_off += chunk;
        n       -= chunk;
    }
}
