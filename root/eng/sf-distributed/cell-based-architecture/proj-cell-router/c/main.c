#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_CELLS 64
#define MAX_TENANT_LEN 64
#define SHUFFLE_K 3

typedef enum {
    CELL_STATE_INACTIVE = 0,
    CELL_STATE_ACTIVE = 1,
    CELL_STATE_DRAINING = 2,
    CELL_STATE_UNHEALTHY = 3
} cell_state_t;

typedef struct {
    uint32_t cell_id;
    char endpoint[128];
    cell_state_t state;
    uint32_t active_connections;
} cell_descriptor_t;

typedef struct {
    cell_descriptor_t cells[MAX_CELLS];
    size_t cell_count;
} cell_router_t;

/* 64-бітний алгоритм хешування FNV-1a */
static uint64_t fnv1a_hash(const char *str, size_t len) {
    uint64_t hash = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint8_t)str[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

/* Ініціалізація маршрутизатора */
void cell_router_init(cell_router_t *router) {
    memset(router, 0, sizeof(cell_router_t));
}

/* Реєстрація комірки */
bool cell_router_add_cell(cell_router_t *router, uint32_t cell_id,
                          const char *endpoint, cell_state_t state) {
    if (router->cell_count >= MAX_CELLS) {
        return false;
    }
    cell_descriptor_t *cell = &router->cells[router->cell_count++];
    cell->cell_id = cell_id;
    snprintf(cell->endpoint, sizeof(cell->endpoint), "%s", endpoint);
    cell->state = state;
    cell->active_connections = 0;
    return true;
}

/* 1. Пряма маршрутизація: один орендар -> одна активна комірка */
const cell_descriptor_t* cell_route_direct(const cell_router_t *router,
                                           const char *tenant_id) {
    if (router->cell_count == 0) {
        return NULL;
    }
    uint64_t h = fnv1a_hash(tenant_id, strlen(tenant_id));
    size_t start_idx = (size_t)(h % router->cell_count);

    /* Лінійне зондування у разі збою основної комірки */
    for (size_t i = 0; i < router->cell_count; ++i) {
        size_t idx = (start_idx + i) % router->cell_count;
        const cell_descriptor_t *cell = &router->cells[idx];
        if (cell->state == CELL_STATE_ACTIVE) {
            return cell;
        }
    }
    return NULL;
}

/* 2. Перемішане шардування (Shuffle Sharding): обрання K унікальних комірок */
const cell_descriptor_t* cell_route_shuffle(const cell_router_t *router,
                                            const char *tenant_id,
                                            size_t k_subset) {
    if (router->cell_count == 0 || k_subset == 0 || k_subset > router->cell_count) {
        return NULL;
    }

    uint64_t seed = fnv1a_hash(tenant_id, strlen(tenant_id));
    uint32_t chosen_indices[MAX_CELLS];
    size_t chosen_count = 0;

    /* Детермінований вибір K унікальних комірок для орендаря */
    uint64_t state = seed;
    while (chosen_count < k_subset) {
        /* Лінійний конгруентний генератор псевдовипадкових чисел */
        state = state * 6364136223846793005ULL + 1442695040888963407ULL;
        uint32_t candidate = (uint32_t)((state >> 32) % router->cell_count);

        bool duplicate = false;
        for (size_t j = 0; j < chosen_count; ++j) {
            if (chosen_indices[j] == candidate) {
                duplicate = true;
                break;
            }
        }
        if (!duplicate) {
            chosen_indices[chosen_count++] = candidate;
        }
    }

    /* Вибір найбільш здорової та найменш завантаженої комірки з виділених K */
    const cell_descriptor_t *best_cell = NULL;
    uint32_t min_connections = UINT32_MAX;

    for (size_t i = 0; i < chosen_count; ++i) {
        const cell_descriptor_t *cell = &router->cells[chosen_indices[i]];
        if (cell->state == CELL_STATE_ACTIVE) {
            if (cell->active_connections < min_connections) {
                min_connections = cell->active_connections;
                best_cell = cell;
            }
        }
    }

    return best_cell;
}
