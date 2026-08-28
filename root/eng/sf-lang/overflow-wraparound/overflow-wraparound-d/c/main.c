#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint8_t count = 255;     // беззнаковий байт: межа 255
    count = count + 1;       // 256 не влазить → лишається 8 молодших бітів
    printf("%u\n", count);   // 0   (визначено: модуль 2^8)

    int8_t  temp  = 127;     // знаковий байт: межа +127
    temp = temp + 1;         // на рівні бітів 10000000, але в C це UB
    printf("%d\n", temp);    // зазвичай -128 — та покладатися НЕ можна

    return 0;
}
