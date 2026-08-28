#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <stdatomic.h>

#define MAGLEV_M 65537u  /* Просте число Ферма 2^16 + 1 */
#define MAX_BACKENDS 64

typedef struct {
    char name[64];
    uint32_t offset;
    uint32_t skip;
    uint32_t weight;
    bool is_alive;
} Backend;

typedef struct {
    int32_t lookup[MAGLEV_M];
    uint32_t generation;
} MaglevTable;

typedef struct {
    Backend backends[MAX_BACKENDS];
    uint32_t num_backends;
    _Atomic(MaglevTable*) active_table;
    MaglevTable table_buffers[2];
    uint32_t current_buffer_idx;
} MaglevRouter;

/* Швидкий некриптографічний 32-бітний хеш FNV-1a */
static inline uint32_t fnv1a_32(const void *data, size_t len, uint32_t seed) {
    const uint8_t *ptr = (const uint8_t*)data;
    uint32_t hash = 2166136261u ^ seed;
    for (size_t i = 0; i < len; ++i) {
        hash ^= ptr[i];
        hash *= 16777619u;
    }
    return hash;
}

/* Обчислення хешу 5-tuple для вхідного IP-пакета */
static inline uint32_t hash_5tuple(uint32_t src_ip, uint32_t dst_ip,
                                   uint16_t src_port, uint16_t dst_port,
                                   uint8_t proto) {
    uint32_t h = src_ip;
    h ^= (dst_ip << 1) | (dst_ip >> 31);
    h ^= ((uint32_t)src_port << 16) | dst_port;
    h ^= (uint32_t)proto * 0x5bd1e995u;
    h ^= h >> 13;
    h *= 0x5bd1e995u;
    h ^= h >> 15;
    return h;
}

void maglev_router_init(MaglevRouter *r) {
    memset(r, 0, sizeof(*r));
    r->num_backends = 0;
    r->current_buffer_idx = 0;

    for (uint32_t i = 0; i < MAGLEV_M; ++i) {
        r->table_buffers[0].lookup[i] = -1;
        r->table_buffers[1].lookup[i] = -1;
    }
    atomic_store_explicit(&r->active_table, &r->table_buffers[0], memory_order_release);
}

bool maglev_add_backend(MaglevRouter *r, const char *name, uint32_t weight) {
    if (r->num_backends >= MAX_BACKENDS) return false;

    uint32_t idx = r->num_backends++;
    Backend *b = &r->backends[idx];
    strncpy(b->name, name, sizeof(b->name) - 1);
    b->name[sizeof(b->name) - 1] = '\0';
    b->weight = (weight == 0) ? 1 : weight;
    b->is_alive = true;

    /* Обчислення offset та skip за двома різними сідами */
    size_t name_len = strlen(b->name);
    b->offset = fnv1a_32(b->name, name_len, 0x9e3779b9u) % MAGLEV_M;
    b->skip = (fnv1a_32(b->name, name_len, 0x85ebca6bu) % (MAGLEV_M - 1)) + 1;

    return true;
}

void maglev_set_backend_state(MaglevRouter *r, uint32_t idx, bool alive) {
    if (idx < r->num_backends) {
        r->backends[idx].is_alive = alive;
    }
}

/* Побудова таблиці у фоновому буфері з урахуванням ваг */
void maglev_rebuild_table(MaglevRouter *r) {
    uint32_t next_buf_idx = 1 - r->current_buffer_idx;
    MaglevTable *target = &r->table_buffers[next_buf_idx];

    for (uint32_t i = 0; i < MAGLEV_M; ++i) {
        target->lookup[i] = -1;
    }

    uint32_t next[MAX_BACKENDS] = {0};
    uint32_t filled = 0;

    while (filled < MAGLEV_M) {
        bool any_progress = false;

        for (uint32_t i = 0; i < r->num_backends; ++i) {
            if (!r->backends[i].is_alive) continue;

            /* Сервер із вагою W претендує на W комірок за один раунд */
            for (uint32_t w = 0; w < r->backends[i].weight; ++w) {
                while (true) {
                    uint32_t c = (r->backends[i].offset + next[i] * r->backends[i].skip) % MAGLEV_M;
                    next[i]++;

                    if (target->lookup[c] == -1) {
                        target->lookup[c] = (int32_t)i;
                        filled++;
                        any_progress = true;
                        break;
                    }
                }
                if (filled == MAGLEV_M) break;
            }
            if (filled == MAGLEV_M) break;
        }

        if (!any_progress && filled < MAGLEV_M) {
            /* Усі бекенди вимкнено або аварійний стан */
            break;
        }
    }

    target->generation++;
    r->current_buffer_idx = next_buf_idx;

    /* Атомарна підміна таблиці для читачів без зупинки Fast Path */
    atomic_store_explicit(&r->active_table, target, memory_order_release);
}

/* Fast Path: вибір бекенда для вхідного пакета */
static inline int32_t maglev_dispatch(const MaglevRouter *r,
                                      uint32_t src_ip, uint32_t dst_ip,
                                      uint16_t src_port, uint16_t dst_port,
                                      uint8_t proto) {
    const MaglevTable *tbl = atomic_load_explicit(&r->active_table, memory_order_acquire);
    if (!tbl) return -1;

    uint32_t h = hash_5tuple(src_ip, dst_ip, src_port, dst_port, proto);
    uint32_t slot = h % MAGLEV_M;
    return tbl->lookup[slot];
}

int main(void) {
    MaglevRouter router;
    maglev_router_init(&router);

    maglev_add_backend(&router, "srv-app-01.dc1", 1);
    maglev_add_backend(&router, "srv-app-02.dc1", 1);
    maglev_add_backend(&router, "srv-app-03.dc1", 2); /* Подвійна вага */
    maglev_add_backend(&router, "srv-app-04.dc1", 1);

    maglev_rebuild_table(&router);

    printf("Таблицю Maglev згенеровано на %u комірок.\n", MAGLEV_M);

    /* Тестова диспетчеризація клієнтського потоку */
    uint32_t client_ip = 0xC0000205; /* 192.0.2.5 */
    uint32_t vip = 0xC6336401;       /* 198.51.100.1 */
    uint16_t client_port = 49152;
    uint16_t vip_port = 443;
    uint8_t proto = 6; /* TCP */

    int32_t target_idx = maglev_dispatch(&router, client_ip, vip, client_port, vip_port, proto);
    if (target_idx >= 0) {
        printf("Клієнтський потік спрямовано на бекенд [%s] (вага: %u)\n",
               router.backends[target_idx].name,
               router.backends[target_idx].weight);
    }

    return 0;
}
