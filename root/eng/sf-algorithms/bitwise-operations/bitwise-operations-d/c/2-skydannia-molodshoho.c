#include <stdint.h>

int count_set_bits(uint64_t x) {
    int count = 0;
    while (x != 0) {
        x &= (x - 1); // скидаємо чергову молодшу одиницю
        count++;
    }
    return count;
}
