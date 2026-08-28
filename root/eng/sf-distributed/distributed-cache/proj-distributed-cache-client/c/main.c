#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define FNV_PRIME_32 16777619U
#define FNV_OFFSET_32 2166136261U
#define MAX_VNODES_TOTAL 4096
#define MAX_SERVERS 32

/* 32-бітний швидкий некриптографічний алгоритм FNV-1a */
static uint32_t fnv1a_hash(const char *key, size_t len) {
    uint32_t hash = FNV_OFFSET_32;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint8_t)key[i];
        hash *= FNV_PRIME_32;
    }
    return hash;
}

typedef struct {
    char host[64];
    int port;
} ServerNode;

typedef struct {
    uint32_t hash;
    size_t server_index;
} VNodeEntry;

typedef struct {
    ServerNode servers[MAX_SERVERS];
    size_t server_count;
    VNodeEntry ring[MAX_VNODES_TOTAL];
    size_t ring_size;
} HashRing;

/* Функція порівняння для впорядкування віртуальних вузлів */
static int compare_vnodes(const void *a, const void *b) {
    const VNodeEntry *va = (const VNodeEntry *)a;
    const VNodeEntry *vb = (const VNodeEntry *)b;
    if (va->hash < vb->hash) return -1;
    if (va->hash > vb->hash) return 1;
    return 0;
}

void hash_ring_init(HashRing *ring) {
    ring->server_count = 0;
    ring->ring_size = 0;
}

bool hash_ring_add_server(HashRing *ring, const char *host, int port, size_t vnodes_per_server) {
    if (ring->server_count >= MAX_SERVERS) return false;
    if (ring->ring_size + vnodes_per_server > MAX_VNODES_TOTAL) return false;

    size_t s_idx = ring->server_count++;
    strncpy(ring->servers[s_idx].host, host, sizeof(ring->servers[s_idx].host) - 1);
    ring->servers[s_idx].host[sizeof(ring->servers[s_idx].host) - 1] = '\0';
    ring->servers[s_idx].port = port;

    char vnode_key[128];
    for (size_t v = 0; v < vnodes_per_server; ++v) {
        snprintf(vnode_key, sizeof(vnode_key), "%s:%d#%zu", host, port, v);
        uint32_t h = fnv1a_hash(vnode_key, strlen(vnode_key));
        ring->ring[ring->ring_size++] = (VNodeEntry){ .hash = h, .server_index = s_idx };
    }

    qsort(ring->ring, ring->ring_size, sizeof(VNodeEntry), compare_vnodes);
    return true;
}

/* Двійковий пошук першого вузла на кільці з hash >= key_hash */
const ServerNode* hash_ring_lookup(const HashRing *ring, const char *key, size_t key_len) {
    if (ring->ring_size == 0) return NULL;

    uint32_t target = fnv1a_hash(key, key_len);
    size_t left = 0;
    size_t right = ring->ring_size;

    while (left < right) {
        size_t mid = left + (right - left) / 2;
        if (ring->ring[mid].hash >= target) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }

    /* Якщо дійшли кінця кола — беремо нульовий вузол (замкнене кільце) */
    size_t chosen_idx = (left == ring->ring_size) ? 0 : left;
    return &ring->servers[ring->ring[chosen_idx].server_index];
}

/* Форматування командного рядка Memcached ASCII */
size_t format_memcached_set(char *buf, size_t max_len, const char *key, const char *val, uint32_t ttl) {
    size_t val_len = strlen(val);
    return snprintf(buf, max_len, "set %s 0 %u %zu\r\n%s\r\n", key, ttl, val_len, val);
}

size_t format_memcached_get(char *buf, size_t max_len, const char *key) {
    return snprintf(buf, max_len, "get %s\r\n", key);
}

int main(void) {
    HashRing ring;
    hash_ring_init(&ring);

    hash_ring_add_server(&ring, "10.0.1.10", 11211, 128);
    hash_ring_add_server(&ring, "10.0.1.11", 11211, 128);
    hash_ring_add_server(&ring, "10.0.1.12", 11211, 128);

    const char *test_keys[] = {"user:101:profile", "session:token_abc", "cart:items_998"};
    char cmd_buf[512];

    for (size_t i = 0; i < 3; ++i) {
        const ServerNode *node = hash_ring_lookup(&ring, test_keys[i], strlen(test_keys[i]));
        format_memcached_get(cmd_buf, sizeof(cmd_buf), test_keys[i]);
        printf("Ключ '%s' -> Вузол %s:%d | Команда: %s", test_keys[i], node->host, node->port, cmd_buf);
    }

    return 0;
}
