#include <stdint.h>
#include <stdio.h>

int main(void) {
    uint16_t price  = 0;     // комірка «сума», поки 0
    uint16_t item   = 45;    // ціна однієї деталі

    price = item;            // поклади в price вміст item → price = 45
    price = price + item;    // праворуч 45+45=90, кладемо в price → price = 90
    price = price + 20;      // праворуч 90+20=110, кладемо в price → price = 110

    printf("Разом: %u\n", price);   // Разом: 110
    return 0;
}
