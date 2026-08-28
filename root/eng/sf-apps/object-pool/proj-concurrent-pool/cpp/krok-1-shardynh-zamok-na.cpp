#include <atomic>
#include <sched.h>

constexpr int SHARDS = 64;                 // степінь двійки → маска замість %

struct alignas(64) Shard {                 // ← кожен шард на СВОЄМУ рядку кеша (крок 6)
    LockFreeStack free;                    // список вільних (замок або без — крок 3)
};
Shard shards[SHARDS];

inline Shard& my_shard() {
    unsigned cpu = sched_getcpu();         // на якому ядрі я зараз — підказка
    return shards[cpu & (SHARDS - 1)];     // дешева маска, бо SHARDS — степінь 2
}
