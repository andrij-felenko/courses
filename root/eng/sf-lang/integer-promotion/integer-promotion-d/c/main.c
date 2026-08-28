#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint8_t port = 0x5a;              // 0101 1010
    uint8_t result = (~port) >> 4;    // намір: інвертувати 8 бітів і зсунути

    printf("0x%02x\n", result);       // очікуємо 0x0a — а буде 0xfa
    return 0;
}
