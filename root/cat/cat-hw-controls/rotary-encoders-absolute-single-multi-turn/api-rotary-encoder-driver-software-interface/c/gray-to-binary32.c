#include <stdint.h>

// Швидке безрозгалужене перетворення 32-бітного коду Ґрея у двійковий
uint32_t gray_to_binary32(uint32_t gray) {
    gray ^= (gray >> 1);
    gray ^= (gray >> 2);
    gray ^= (gray >> 4);
    gray ^= (gray >> 8);
    gray ^= (gray >> 16);
    return gray;
}

// Повільне циклічне перетворення для довільної розрядності N
uint32_t gray_to_binary_generic(uint32_t gray, uint8_t bit_width) {
    uint32_t mask = gray >> 1;
    while (mask != 0) {
        gray ^= mask;
        mask >>= 1;
    }
    return gray & ((1UL << bit_width) - 1);
}
