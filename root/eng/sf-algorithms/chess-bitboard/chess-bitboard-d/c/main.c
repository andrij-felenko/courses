#include <stdint.h>

void handle_element(int sq);

void process_bitboard(uint64_t bb) {
    while (bb != 0) {
        int sq = __builtin_ctzll(bb); /* 1. Отримуємо індекс чергового елемента */
        handle_element(sq);           /* 2. Обробляємо елемент */
        bb &= (bb - 1);               /* 3. Скидаємо молодший біт за 1 такт */
    }
}
