#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define NODE_COUNT 10000000

/* 1. Класичний вузол з 64-бітним покажчиком (16 байтів через вирівнювання) */
struct RawNode {
    uint32_t value;
    struct RawNode* next;
};

/* 2. Компактний вузол з 32-бітним індексом арени (8 байтів) */
struct CompactNode {
    uint32_t value;
    uint32_t next_idx;
};

#define NULL_INDEX UINT32_MAX

/* Послідовний обхід списку на сирих покажчиках */
static uint64_t traverse_raw(const struct RawNode* head) {
    uint64_t sum = 0;
    const struct RawNode* curr = head;
    while (curr != NULL) {
        sum += curr->value;
        curr = curr->next;
    }
    return sum;
}

/* Послідовний обхід компактного індексного списку */
static uint64_t traverse_compact(const struct CompactNode* arena, uint32_t head_idx) {
    uint64_t sum = 0;
    uint32_t curr = head_idx;
    while (curr != NULL_INDEX) {
        sum += arena[curr].value;
        curr = arena[curr].next_idx;
    }
    return sum;
}

int main(void) {
    printf("Розмір RawNode (64-бітні покажчики): %zu байтів\n", sizeof(struct RawNode));
    printf("Розмір CompactNode (32-бітний індекс): %zu байтів\n\n", sizeof(struct CompactNode));

    /* Виділення пам'яті для списку на сирих покажчиках */
    struct RawNode* raw_nodes = (struct RawNode*)malloc(NODE_COUNT * sizeof(struct RawNode));
    if (!raw_nodes) return 1;

    for (uint32_t i = 0; i < NODE_COUNT; ++i) {
        raw_nodes[i].value = i;
        raw_nodes[i].next = (i + 1 < NODE_COUNT) ? &raw_nodes[i + 1] : NULL;
    }

    /* Виділення пам'яті для компактної арени */
    struct CompactNode* compact_arena = (struct CompactNode*)malloc(NODE_COUNT * sizeof(struct CompactNode));
    if (!compact_arena) {
        free(raw_nodes);
        return 1;
    }

    for (uint32_t i = 0; i < NODE_COUNT; ++i) {
        compact_arena[i].value = i;
        compact_arena[i].next_idx = (i + 1 < NODE_COUNT) ? (i + 1) : NULL_INDEX;
    }

    /* Замір часу обходу сирого списку */
    clock_t start_raw = clock();
    uint64_t sum_raw = traverse_raw(&raw_nodes[0]);
    clock_t end_raw = clock();
    double time_raw = (double)(end_raw - start_raw) / CLOCKS_PER_SEC;

    /* Замір часу обходу компактного списку */
    clock_t start_compact = clock();
    uint64_t sum_compact = traverse_compact(compact_arena, 0);
    clock_t end_compact = clock();
    double time_compact = (double)(end_compact - start_compact) / CLOCKS_PER_SEC;

    printf("Raw Node:     сума = %llu, час = %.4f с (пам'ять = %.1f МБ)\n",
           (unsigned long long)sum_raw, time_raw,
           (double)(NODE_COUNT * sizeof(struct RawNode)) / (1024.0 * 1024.0));

    printf("Compact Node: сума = %llu, час = %.4f с (пам'ять = %.1f МБ)\n",
           (unsigned long long)sum_compact, time_compact,
           (double)(NODE_COUNT * sizeof(struct CompactNode)) / (1024.0 * 1024.0));

    free(raw_nodes);
    free(compact_arena);
    return 0;
}
