#include <cstdint>
#include <atomic>

// ЛІК: кожен лічильник вирівняний на межу кеш-лінії (64 байти) → своя лінія
struct alignas(64) PaddedCounter {         // C++11: вирівняти на 64 байти
    std::atomic<int64_t> value{0};
};

static PaddedCounter counters[4];          // тепер кожен — в окремій лінії

void worker(int core) {
    for (int64_t i = 0; i < 100000000; i++)
        counters[core].value++;            // ядра чіпають РІЗНІ лінії — гонки лінії нема
}
