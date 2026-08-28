#include <iostream>
#include <cstdint>
#include <bit>

int main() {
    // Вхідний рядок (16 байтів):  { "a" : [ 1 , 2 ] }
    // Позиції токенів:            0 123 4 5 6 7 8 9 0
    constexpr std::uint64_t candidate_mask = (1ULL << 0) | (1ULL << 4) | (1ULL << 5) | 
                                             (1ULL << 7) | (1ULL << 9) | (1ULL << 10);
    constexpr std::uint64_t in_string_mask = (1ULL << 2); // 'a' всередині лапок

    // Фільтрація структури однією операцією над бітовою маскою
    std::uint64_t structural_mask = candidate_mask & (~in_string_mask);

    std::cout << "Знайдені індекси структурних токенів: ";
    while (structural_mask != 0) {
        const int idx = std::countr_zero(structural_mask); // C++20 count trailing zeros
        std::cout << idx << " ";
        structural_mask &= (structural_mask - 1); // Скидання молодшого встановленого біта
    }
    std::cout << "\n";

    return 0;
}
