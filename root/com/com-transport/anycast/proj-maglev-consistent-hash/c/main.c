#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define MAGLEV_M 65537  /* Просте число для розміру таблиці */
#define MAX_BACKENDS 16

typedef struct {
    char name[32];
    uint32_t offset;
    uint32_t skip;
    uint32_t next_idx;
    bool is_alive;
} Backend;

typedef struct {
    Backend backends[MAX_BACKENDS];
    int num_backends;
    int lookup_table[MAGLEV_M];
} Maglev;

/* 32-бітний хеш FNV-1a */
static uint32_t fnv1a(const char *str, uint32_t seed) {
    uint32_t hash = 2166136261u ^ seed;
    while (*str) {
        hash ^= (uint8_t)(*str++);
        hash *= 16777619u;
    }
    return hash;
}

/* 5-tuple хешування клієнтського пакета */
static uint32_t hash_5tuple(uint32_t src_ip, uint32_t dst_ip, 
                            uint16_t src_port, uint16_t dst_port, uint8_t proto) {
    uint32_t h = src_ip;
    h ^= (dst_ip << 1) | (dst_ip >> 31);
    h ^= ((uint32_t)src_port << 16) | dst_port;
    h ^= (uint32_t)proto * 0x5bd1e995;
    h ^= h >> 13;
    h *= 0x5bd1e995;
    h ^= h >> 15;
    return h;
}

void maglev_init(Maglev *m) {
    m->num_backends = 0;
    for (int i = 0; i < MAGLEV_M; ++i) {
        m->lookup_table[i] = -1;
    }
}

void maglev_add_backend(Maglev *m, const char *name) {
    if (m->num_backends >= MAX_BACKENDS) return;
    int idx = m->num_backends++;
    strncpy(m->backends[idx].name, name, sizeof(m->backends[idx].name) - 1);
    m->backends[idx].name[sizeof(m->backends[idx].name) - 1] = '\0';
    m->backends[idx].is_alive = true;

    /* Обчислюємо offset та skip за двома різними сідами */
    m->backends[idx].offset = fnv1a(name, 0x12345678) % MAGLEV_M;
    m->backends[idx].skip = (fnv1a(name, 0x87654321) % (MAGLEV_M - 1)) + 1;
}

void maglev_rebuild_table(Maglev *m) {
    for (int i = 0; i < MAGLEV_M; ++i) {
        m->lookup_table[i] = -1;
    }
    for (int i = 0; i < m->num_backends; ++i) {
        m->backends[i].next_idx = 0;
    }

    int filled = 0;
    while (filled < MAGLEV_M) {
        for (int i = 0; i < m->num_backends; ++i) {
            if (!m->backends[i].is_alive) continue;

            uint32_t offset = m->backends[i].offset;
            uint32_t skip = m->backends[i].skip;
            uint32_t j = m->backends[i].next_idx;

            while (true) {
                uint32_t candidate = (offset + j * skip) % MAGLEV_M;
                j++;
                if (m->lookup_table[candidate] == -1) {
                    m->lookup_table[candidate] = i;
                    m->backends[i].next_idx = j;
                    filled++;
                    break;
                }
            }
            if (filled == MAGLEV_M) break;
        }
    }
}

int maglev_dispatch(const Maglev *m, uint32_t src_ip, uint32_t dst_ip,
                    uint16_t src_port, uint16_t dst_port, uint8_t proto) {
    uint32_t h = hash_5tuple(src_ip, dst_ip, src_port, dst_port, proto);
    uint32_t idx = h % MAGLEV_M;
    return m->lookup_table[idx];
}

int main(void) {
    Maglev m;
    maglev_init(&m);
    maglev_add_backend(&m, "srv-app-01.eu-central");
    maglev_add_backend(&m, "srv-app-02.eu-central");
    maglev_add_backend(&m, "srv-app-03.eu-central");
    maglev_add_backend(&m, "srv-app-04.eu-central");

    maglev_rebuild_table(&m);

    printf("Таблицю Maglev розміром %d успішно заповнено для %d бекендів.\n", MAGLEV_M, m.num_backends);

    /* Тестова диспетчеризація клієнтського потоку */
    uint32_t client_ip = 0xC0000201; /* 192.0.2.1 */
    uint32_t vip = 0xC6336401;       /* 198.51.100.1 */
    uint16_t client_port = 54321;
    uint16_t svc_port = 443;
    uint8_t proto = 6; /* TCP */

    int b_idx = maglev_dispatch(&m, client_ip, vip, client_port, svc_port, proto);
    printf("Пакет від 192.0.2.1:%u спрямовано на бекенд [%s]\n", client_port, m.backends[b_idx].name);

    return 0;
}
