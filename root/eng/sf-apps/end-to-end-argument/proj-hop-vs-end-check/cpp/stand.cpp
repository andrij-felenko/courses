// stand.cpp — збірка: g++ -O2 -std=c++17 stand.cpp -o stand
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <utility>
#include <vector>

constexpr size_t PAYLOAD = 1024;                 // байтів даних у кадрі

struct Frame {
    uint8_t  data[PAYLOAD];
    uint32_t len;
    uint16_t sum;                                // ділянкова перевірка їде в кадрі
};

// Інтернет-контрольна сума (RFC 1071). Байти складаються парами
// у 16-бітові слова, перенос повертається в молодший розряд.
uint16_t checksum16(const uint8_t* p, size_t n) {
    uint32_t s = 0;
    for (size_t i = 0; i + 1 < n; i += 2)
        s += (uint32_t(p[i]) << 8) | p[i + 1];
    if (n & 1)
        s += uint32_t(p[n - 1]) << 8;       // непарний хвіст — як старший байт
    while (s >> 16)
        s = (s & 0xFFFF) + (s >> 16);       // згортаємо перенос
    return uint16_t(~s);
}
