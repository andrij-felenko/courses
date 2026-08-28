#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint8_t a = 200, b = 200;
    uint8_t r = a * b;            // очікуєш «модуль 256»?
    // насправді: a,b → int; 200*200 = 40000 (в int, влазить);
    // потім 40000 присвоюється uint8_t → аж ТУТ модуль 256 → 64
    printf("%u\n", r);           // 64

    uint16_t x = 50000, y = 50000;
    uint32_t big = x * y;        // x,y → int; 2.5 млрд > INT_MAX → UB!
    printf("%u\n", big);         // формально невизначено
    return 0;
}
