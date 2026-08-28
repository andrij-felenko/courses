#include <stdint.h>

// Повертає: +1 якщо a>b,  0 якщо a==b,  -1 якщо a<b.
// Свідомо скановано побітово від старшого біта — так само, як каскад у залізі.
int cmp16_bitwise(uint16_t a, uint16_t b) {
    for (int i = 15; i >= 0; --i) {          // біт 15 = старший
        uint16_t mask = (uint16_t)(1u << i);
        uint16_t abit = a & mask;
        uint16_t bbit = b & mask;
        if (abit != bbit)                     // перша відмінність
            return (abit > bbit) ? +1 : -1;   // чий біт «1» — той більший
    }
    return 0;                                 // жодної відмінності — рівні
}
