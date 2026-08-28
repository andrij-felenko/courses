#include <stdio.h>

int main(void) {
    uint8_t s = 0x1u;            // старт: 0001 (аби не заборонений 0000)
    for (int i = 0; i < 15; i++) {
        int out_bit = (s >> 3) & 1;   // знімаємо старший біт як вихід
        printf("%d ", out_bit);
        s = lfsr4_step(s);
    }
    // Надрукує:  0 0 0 1 1 1 1 0 1 0 1 1 0 0 1
    return 0;
}
