// c++ -std=c++20 -O2 chan.cpp && ./a.out
#include <bit>
#include <cstdint>
#include <cstdio>
#include <limits>

constexpr uint8_t kChannels = 16;
constexpr uint8_t kInvalid  = std::numeric_limits<uint8_t>::max();

static uint32_t g_used = 1;                     // біт 0 зарезервовано

static uint8_t take()
{
    for (uint8_t i = 0; i < kChannels; ++i) {
        if (g_used & (1u << i)) { continue; }
        g_used |= (1u << i);
        return i;
    }
    return kInvalid;
}

static void give(uint8_t ch)
{
    if (ch == kInvalid) { return; }
    g_used &= ~(1u << ch);
}

static int freeCount() { return std::popcount(~g_used & 0xFFFFu); }

int main()
{
    const uint8_t a = take();            // 1
    const uint8_t b = take();            // 2
    give(a);
    const uint8_t c = take();            // знову 1 — номер перевикористано
    printf("a=%u b=%u c=%u  маска=0x%04X  вільних=%d\n",
           (unsigned)a, (unsigned)b, (unsigned)c, (unsigned)g_used, freeCount());

    give(c);                             // власник повернув свій номер
    const uint8_t d = take();            // сусід узяв той самий номер
    give(c);                             // спізніла копія власника віддає його ВДРУГЕ
    const uint8_t e = take();            // і номер видають ще раз
    printf("d=%u e=%u  → два зʼєднання на каналі %u\n",
           (unsigned)d, (unsigned)e, (unsigned)d);

    for (int i = 0; i < 13; ++i) { (void)take(); }   // беремо й «забуваємо» повернути
    printf("після витоку маска=0x%04X  вільних=%d\n", (unsigned)g_used, freeCount());
    printf("наступна видача дає %u — це 0xFF, каналів більше нема\n", (unsigned)take());
    return 0;
}
