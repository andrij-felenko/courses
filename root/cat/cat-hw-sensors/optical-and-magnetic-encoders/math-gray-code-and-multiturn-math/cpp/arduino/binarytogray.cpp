#include <Arduino.h>

// Пряме перетворення: Binary -> Gray
uint32_t binaryToGray(uint32_t binary) {
    return binary ^ (binary >> 1);
}

// Обернене перетворення: Gray -> Binary
uint32_t grayToBinary(uint32_t gray) {
    gray ^= (gray >> 1);
    gray ^= (gray >> 2);
    gray ^= (gray >> 4);
    gray ^= (gray >> 8);
    gray ^= (gray >> 16);
    return gray;
}
