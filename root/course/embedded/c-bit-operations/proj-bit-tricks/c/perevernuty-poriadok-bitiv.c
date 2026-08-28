#include <stdint.h>

uint32_t reverse_bits(uint32_t x) {
    x = ((x & 0x55555555) << 1)  | ((x & 0xAAAAAAAA) >> 1);   // обмін сусідніх бітів
    x = ((x & 0x33333333) << 2)  | ((x & 0xCCCCCCCC) >> 2);   // обмін сусідніх пар
    x = ((x & 0x0F0F0F0F) << 4)  | ((x & 0xF0F0F0F0) >> 4);   // обмін четвірок
    x = ((x & 0x00FF00FF) << 8)  | ((x & 0xFF00FF00) >> 8);   // обмін байтів
    x = ((x & 0x0000FFFF) << 16) | ((x & 0xFFFF0000) >> 16);  // обмін половин
    return x;
}
