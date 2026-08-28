#include <cstdint>
#include <bit>      // std::popcount (C++20)

// відстань Гаммінга двох 256-бітних ORB-дескрипторів (8 слів по 32 біти)
int hamming256(const uint32_t a[8], const uint32_t b[8]) {
    int dist = 0;
    for (int i = 0; i < 8; ++i)
        dist += std::popcount(a[i] ^ b[i]);  // XOR → лічба різних бітів
    return dist;                             // 0 = однакові, 256 = усе навпаки
}

// для кожного дескриптора ліворуч знайти найближчий і другий праворуч,
// прийняти лише за пробою відношення (для Гаммінга — теж відношення відстаней)
int match_one(const uint32_t query[8],
              const uint32_t train[][8], int m,
              float ratio) {
    int best = 1 << 30, second = 1 << 30, best_j = -1;
    for (int j = 0; j < m; ++j) {
        int d = hamming256(query, train[j]);
        if (d < best) { second = best; best = d; best_j = j; }
        else if (d < second) { second = d; }
    }
    // збіг певний, лише коли найкращий помітно ближчий за другий
    if (second > 0 && (float)best < ratio * (float)second)
        return best_j;      // прийнято
    return -1;              // неоднозначно — відкинути
}
