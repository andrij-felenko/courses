#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

// Погано: обидва лічильники лежать на одному 64-байтовому кеш-рядку.
// Модифікація counter_a інвалідує counter_b для іншого ядра (False Sharing).
struct UnalignedCounters {
    uint64_t counter_a;
    uint64_t counter_b;
};

// Добре: кожен лічильник вирівняно за межею кеш-рядка (64 байти).
// Кожне ядро працює з власним кеш-рядком без Cache Line Bouncing.
struct AlignedCounters {
    _Alignas(64) uint64_t counter_a;
    _Alignas(64) uint64_t counter_b;
};
