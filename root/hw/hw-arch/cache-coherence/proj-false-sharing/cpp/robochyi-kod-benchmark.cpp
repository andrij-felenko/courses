#include <cstdint>
#include <cstddef>
#include <thread>
#include <vector>
#include <chrono>
#include <cstdio>

constexpr int      N     = 4;            // потоків = ядер, під якими міряємо
constexpr int64_t  ITERS = 200'000'000;  // ітерацій на потік (щоб час був відчутний)
constexpr size_t   LINE  = 64;           // припущення про розмір лінії (див. пастки!)

// ── НАЇВНО: лічильники впритул → усі в одній-двох лініях ──
struct NaiveCounters {
    int64_t v[N];                        // 4×8 = 32 байти → одна 64-байтова лінія
};

// ── ЛІК: кожен лічильник вирівняний на межу лінії → своя лінія ──
struct alignas(LINE) PaddedCounter {     // C++11: вся структура вирівняна на 64
    int64_t value;
    // компілятор сам добиває структуру до 64 байтів (sizeof == 64),
    // бо масив таких структур має тримати вирівнювання кожного елемента
};
