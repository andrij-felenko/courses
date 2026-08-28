#include <cstdint>
#include <bit>      // std::popcount (C++20)

// відстань Гаммінга двох 256-бітних ORB-дескрипторів (8 слів по 32 біти)
int hamming256(const uint32_t a[8], const uint32_t b[8]) {
    int dist = 0;
    for (int i = 0; i < 8; ++i)
        dist += std::popcount(a[i] ^ b[i]);   // XOR → лічба розбіжних бітів
    return dist;                              // 0 = однакові, 256 = усе навпаки
}
