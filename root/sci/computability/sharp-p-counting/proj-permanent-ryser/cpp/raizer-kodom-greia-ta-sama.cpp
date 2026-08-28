#include <vector>
#include <bit>          // std::countr_zero, std::popcount (C++20)
#include <cstdint>

// Формула Райзера з обходом підмножин кодом Ґрея. Складність O(2ⁿ · n). n ≤ 63.
template <class T>
T perm_ryser(const std::vector<std::vector<T>>& A) {
    int n = (int)A.size();
    std::vector<T> rowsum(n, T(0));            // rowsumᵢ = Σ_{j∈S} A[i][j] для поточної S
    T total = 0;
    uint64_t prev = 0;                         // код Ґрея попередньої підмножини; старт — S = ∅
    for (uint64_t k = 1; k < (1ull << n); ++k) {
        uint64_t gray = k ^ (k >> 1);          // маска k-ї підмножини в порядку Ґрея
        int j = std::countr_zero(gray ^ prev); // єдиний стовпець, що перемкнувся
        if ((gray >> j) & 1)                   // біт став 1 — стовпець j увійшов у S
            for (int i = 0; i < n; ++i) rowsum[i] += A[i][j];
        else                                   // біт став 0 — стовпець j вийшов із S
            for (int i = 0; i < n; ++i) rowsum[i] -= A[i][j];
        prev = gray;

        T prod = 1;
        for (int i = 0; i < n; ++i) prod *= rowsum[i];    // ∏ᵢ rowsumᵢ

        if (std::popcount(gray) & 1) total -= prod;       // знак доданка = (−1)^|S|
        else                         total += prod;
    }
    return (n & 1) ? -total : total;           // спільний множник (−1)ⁿ перед усією сумою
}
