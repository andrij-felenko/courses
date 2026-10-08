#include <stdint.h>

// Пряме перетворення: Binary -> Gray
uint32_t binary_to_gray(uint32_t binary) {
    return binary ^ (binary >> 1);
}

// Обернене перетворення: Gray -> Binary (32-бітний паралельний алгоритм)
uint32_t gray_to_binary(uint32_t gray) {
    gray ^= (gray >> 1);
    gray ^= (gray >> 2);
    gray ^= (gray >> 4);
    gray ^= (gray >> 8);
    gray ^= (gray >> 16);
    return gray;
}
