#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint8_t a = 0xFB, b = 0x03;      // ті самі два байти
    uint8_t s = a + b;               // сума на рівні бітів: 0xFE

    printf("беззнаково: %u + %u = %u\n",  a, b, s);        // 251 + 3 = 254
    printf("знаково:    %d + %d = %d\n",
           (int8_t)a, (int8_t)b, (int8_t)s);               // −5 + 3 = −2
    return 0;
}
