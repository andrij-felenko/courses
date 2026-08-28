#include <stdint.h>
#include <stdio.h>

// Знакове розширення value з num_bits бітів до повного int32.
int32_t sign_extend(uint32_t value, int num_bits) {
    uint32_t m = (uint32_t)1 << (num_bits - 1);   // біт-знак на місці
    return (int32_t)((value ^ m) - m);            // (v ^ M) − M
}

int main(void) {
    uint16_t raw = 0x0FFF;                 // 12 бітів усі одиниці = −1
    int32_t  a   = sign_extend(raw, 12);
    printf("%d\n", a);                     // −1  (а не 4095!)

    raw = 0x07FF;                          // найбільше додатне 12-бітне
    printf("%d\n", sign_extend(raw, 12));  // 2047

    return 0;
}
