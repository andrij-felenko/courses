#include <stdint.h>

// Один пакований BCD-байт (0x00..0x99) -> число 0..99, без ділення.
uint8_t bcd_byte_to_bin(uint8_t bcd) {
    uint8_t hi = bcd >> 4;                  // старша тетрада — десятки
    uint8_t lo = bcd & 0x0F;                // молодша — одиниці
    return (uint8_t)(hi * 10 + lo);         // десяткова вага старшої = 10
    //     hi*10 = hi*8 + hi*2 = (hi<<3)+(hi<<1) — компілятор так і зробить
}
// bcd_byte_to_bin(0x49) -> 4*10 + 9 = 49
