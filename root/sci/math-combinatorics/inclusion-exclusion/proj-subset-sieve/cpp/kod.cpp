#include <cstdint>
#include <vector>
#include <bit>          // std::popcount (C++20)

// Скільки чисел у [1, N] взаємно прості з усіма простими p[0..r-1]
// (не діляться на жоден). Порожня маска дає весь N — доданок «нуля множин».
int64_t coprime_count(int64_t N, const std::vector<int64_t>& p) {
    int r = (int)p.size();
    int64_t total = 0;
    for (uint32_t mask = 0; mask < (1u << r); ++mask) {
        int64_t prod = 1;
        bool over = false;
        for (int i = 0; i < r; ++i)
            if ((mask >> i) & 1) {
                if (p[i] > N / prod) { over = true; break; }   // добуток перевищив би N
                prod *= p[i];
            }
        int64_t term = over ? 0 : N / prod;                    // ⌊N / добуток⌋
        total += (std::popcount(mask) & 1) ? -term : term;     // знак за парністю розміру
    }
    return total;
}

// Скільки діляться бодай на одне — це просто доповнення.
int64_t divisible_by_any(int64_t N, const std::vector<int64_t>& p) {
    return N - coprime_count(N, p);
}
