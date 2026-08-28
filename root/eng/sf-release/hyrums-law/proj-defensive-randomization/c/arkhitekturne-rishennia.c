#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define MAX_NODES 16
#define NAME_LEN  32

typedef struct {
    char     name[NAME_LEN];
    int      load_percent;
    uint32_t node_id;
} ClusterNode;

typedef struct {
    ClusterNode nodes[MAX_NODES];
    size_t      count;
    unsigned int rng_seed;
    int         defensive_mode; /* 1 = тасувати неспецифікований порядок */
} NodeRegistry;

void registry_init(NodeRegistry *reg, int defensive_mode, unsigned int seed) {
    if (!reg) return;
    reg->count = 0;
    reg->rng_seed = seed ? seed : (unsigned int)time(NULL);
    reg->defensive_mode = defensive_mode;
}

int registry_add(NodeRegistry *reg, const char *name, int load, uint32_t id) {
    if (!reg || !name) return -1;
    if (reg->count >= MAX_NODES) return -1;

    strncpy(reg->nodes[reg->count].name, name, NAME_LEN - 1);
    reg->nodes[reg->count].name[NAME_LEN - 1] = '\0';
    reg->nodes[reg->count].load_percent = load;
    reg->nodes[reg->count].node_id = id;
    reg->count++;
    return 0;
}

/* Отримання вузлів із захисним перемішуванням (Fisher-Yates) */
size_t registry_get_active(NodeRegistry *reg, ClusterNode *out_buf, size_t max_out) {
    if (!reg || !out_buf || max_out == 0) return 0;

    size_t n = (reg->count < max_out) ? reg->count : max_out;
    for (size_t i = 0; i < n; i++) {
        out_buf[i] = reg->nodes[i];
    }

    /* Якщо увімкнено захисний режим і в списку більше одного елемента,
       виконуємо тасування Фішера — Єйтса для дедетермінізації */
    if (reg->defensive_mode && n > 1) {
        for (size_t i = n - 1; i > 0; i--) {
            size_t j = (size_t)(rand_r(&reg->rng_seed) % (i + 1));
            ClusterNode tmp = out_buf[i];
            out_buf[i] = out_buf[j];
            out_buf[j] = tmp;
        }
    }
    return n;
}
