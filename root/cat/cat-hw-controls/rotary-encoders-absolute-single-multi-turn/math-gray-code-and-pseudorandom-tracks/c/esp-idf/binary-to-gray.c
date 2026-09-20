#include <stdint.h>

// Пряме перетворення двійкового коду в код Ґрея
uint32_t binary_to_gray(uint32_t binary) {
    return binary ^ (binary >> 1);
}

// Зворотне перетворення коду Ґрея в двійковий код
uint32_t gray_to_binary(uint32_t gray) {
    uint32_t binary = gray;
    while (gray >>= 1) {
        binary ^= gray;
    }
    return binary;
}
