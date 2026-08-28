#include <cstdint>
#include <atomic>

// НАЇВНО: чотири лічильники впритул → усі в одній кеш-лінії
static std::atomic<int64_t> counters[4];

void worker(int core) {                 // кожне ядро зі своїм core = 0..3
    for (int64_t i = 0; i < 100000000; i++)
        counters[core]++;               // пише лише «свій» елемент…
}                                        // …але лінія одна на всіх — пінг-понг
