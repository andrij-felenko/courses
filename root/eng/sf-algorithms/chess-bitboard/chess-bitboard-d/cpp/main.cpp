#include <cstdint>
#include <bit>

template <typename Callback>
void process_bitboard(uint64_t bb, Callback&& handle_element) {
    while (bb != 0) {
        const int sq = std::countr_zero(bb); /* 1. Отримуємо індекс елемента */
        handle_element(sq);                  /* 2. Обробляємо елемент */
        bb &= (bb - 1);                      /* 3. Скидаємо молодший біт за 1 такт */
    }
}
