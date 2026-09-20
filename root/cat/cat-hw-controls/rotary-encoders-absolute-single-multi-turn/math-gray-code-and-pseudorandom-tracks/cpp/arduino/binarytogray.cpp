#include <Arduino.h>

// Пряме перетворення двійкового коду в код Ґрея
uint32_t binaryToGray(uint32_t binary) {
    return binary ^ (binary >> 1);
}

// Зворотне перетворення коду Ґрея в двійковий код
uint32_t grayToBinary(uint32_t gray) {
    uint32_t binary = gray;
    while (gray >>= 1) {
        binary ^= gray;
    }
    return binary;
}
