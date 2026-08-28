#include <stdint.h>
#include <stdio.h>

int main(void) {
    // намір: пройти індекси 4,3,2,1,0 і спинитись
    for (uint8_t i = 4; i >= 0; i--) {   // i беззнаковий → i >= 0 ЗАВЖДИ істина
        printf("%u ", i);                // 4 3 2 1 0 255 254 253 ... без кінця
    }
    return 0;
}
