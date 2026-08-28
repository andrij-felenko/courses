/* router.c - Високопродуктивний маршрутизатор та Scatter-Gather координатор мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_SHARDS 16
#define MAX_KEY_LEN 64
#define MAX_VAL_LEN 128
#define MAX_ROWS_PER_SHARD 64

/* Хеш-функція FNV-1a 64-bit */
static uint64_t fnv1a_hash(const char *key) {
    uint64_t hash = 14695981039346656037ULL;
    while (*key) {
        hash ^= (uint8_t)(*key++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

/* Структура запису */
typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
} Row;

/* Структура шарда (імітація віддаленого вузла) */
typedef struct {
    int shard_id;
    char node_addr[32];
    Row rows[MAX_ROWS_PER_SHARD];
    size_t row_count;
    char range_start[MAX_KEY_LEN];
    char range_end[MAX_KEY_LEN];
} Shard;

/* Таблиця маршрутизації кластера */
typedef struct {
    Shard shards[MAX_SHARDS];
    size_t num_shards;
    bool use_hash_routing; /* true = Hash Slots, false = Range */
} RoutingTable;

/* Елемент мін-купи для потокового k-канального злиття */
typedef struct {
    Row row;
    int shard_idx;
    size_t next_row_idx;
} HeapNode;

typedef struct {
    HeapNode nodes[MAX_SHARDS];
    size_t size;
} MinHeap;

/* Операції з мін-купою */
static void heap_swap(HeapNode *a, HeapNode *b) {
    HeapNode tmp = *a;
    *a = *b;
    *b = tmp;
}

static void heap_push(MinHeap *h, HeapNode node) {
    size_t i = h->size++;
    h->nodes[i] = node;
    while (i > 0) {
        size_t p = (i - 1) / 2;
        if (strcmp(h->nodes[i].row.key, h->nodes[p].row.key) < 0) {
            heap_swap(&h->nodes[i], &h->nodes[p]);
            i = p;
        } else {
            break;
        }
    }
}

static bool heap_pop(MinHeap *h, HeapNode *out) {
    if (h->size == 0) return false;
    *out = h->nodes[0];
    h->nodes[0] = h->nodes[--h->size];
    size_t i = 0;
    while (true) {
        size_t left = 2 * i + 1, right = 2 * i + 2, smallest = i;
        if (left < h->size && strcmp(h->nodes[left].row.key, h->nodes[smallest].row.key) < 0)
            smallest = left;
        if (right < h->size && strcmp(h->nodes[right].row.key, h->nodes[smallest].row.key) < 0)
            smallest = right;
        if (smallest != i) {
            heap_swap(&h->nodes[i], &h->nodes[smallest]);
            i = smallest;
        } else {
            break;
        }
    }
    return true;
}

/* Маршрутизація точкового запиту */
int route_point_query(const RoutingTable *rt, const char *key) {
    if (rt->num_shards == 0) return -1;

    if (rt->use_hash_routing) {
        uint64_t h = fnv1a_hash(key);
        return (int)(h % rt->num_shards);
    } else {
        /* Бінарний або лінійний пошук за діапазоном */
        for (size_t i = 0; i < rt->num_shards; ++i) {
            if (strcmp(key, rt->shards[i].range_start) >= 0 &&
                strcmp(key, rt->shards[i].range_end) <= 0) {
                return (int)i;
            }
        }
    }
    return -1;
}

/* Вставка запису через маршрутизатор */
bool router_put(RoutingTable *rt, const char *key, const char *val) {
    int target_shard = route_point_query(rt, key);
    if (target_shard < 0 || target_shard >= (int)rt->num_shards) return false;

    Shard *s = &rt->shards[target_shard];
    if (s->row_count >= MAX_ROWS_PER_SHARD) return false;

    /* Вставка з підтриманням впорядкованості за ключем на шарді */
    size_t pos = s->row_count;
    for (size_t i = 0; i < s->row_count; ++i) {
        if (strcmp(key, s->rows[i].key) < 0) {
            pos = i;
            break;
        }
    }
    for (size_t i = s->row_count; i > pos; --i) {
        s->rows[i] = s->rows[i - 1];
    }
    strncpy(s->rows[pos].key, key, MAX_KEY_LEN - 1);
    strncpy(s->rows[pos].value, val, MAX_VAL_LEN - 1);
    s->row_count++;
    return true;
}

/* Потоковий Scatter-Gather SCAN з k-канальним злиттям */
void router_scatter_gather_scan(const RoutingTable *rt,
                                const char *key_start,
                                const char *key_end,
                                size_t limit,
                                size_t offset) {
    printf("=== SCATTER-GATHER SCAN ['%s' .. '%s'] (Limit: %zu, Offset: %zu) ===\n",
           key_start, key_end, limit, offset);

    MinHeap heap = {0};

    /* Фаза Scatter: ініціалізація перших елементів від кожного релевантного шарда */
    for (size_t i = 0; i < rt->num_shards; ++i) {
        const Shard *s = &rt->shards[i];
        /* Для Range перевіряємо перетин діапазонів, для Hash опитуємо всі шарди */
        if (!rt->use_hash_routing) {
            if (strcmp(key_start, s->range_end) > 0 || strcmp(key_end, s->range_start) < 0)
                continue;
        }

        /* Пошук першого запису >= key_start на шарді */
        for (size_t r = 0; r < s->row_count; ++r) {
            if (strcmp(s->rows[r].key, key_start) >= 0 && strcmp(s->rows[r].key, key_end) <= 0) {
                HeapNode hn;
                hn.row = s->rows[r];
                hn.shard_idx = (int)i;
                hn.next_row_idx = r + 1;
                heap_push(&heap, hn);
                break;
            }
        }
    }

    /* Фаза Gather & Streaming K-Way Merge */
    size_t passed = 0, emitted = 0;
    HeapNode top;

    while (heap_pop(&heap, &top)) {
        if (passed >= offset && emitted < limit) {
            printf("  [Знайдено]: Key='%s', Val='%s' (з шарда %d)\n",
                   top.row.key, top.row.value, top.shard_idx);
            emitted++;
        }
        passed++;

        if (emitted >= limit) break;

        /* Підвантажуємо наступний запис із того самого шарда */
        const Shard *s = &rt->shards[top.shard_idx];
        size_t next_idx = top.next_row_idx;
        while (next_idx < s->row_count) {
            if (strcmp(s->rows[next_idx].key, key_end) <= 0) {
                HeapNode next_hn;
                next_hn.row = s->rows[next_idx];
                next_hn.shard_idx = top.shard_idx;
                next_hn.next_row_idx = next_idx + 1;
                heap_push(&heap, next_hn);
                break;
            }
            next_idx++;
        }
    }
    printf("Підсумок: повернуто %zu записів (пропущено offset=%zu)\n\n", emitted, offset);
}

int main(void) {
    RoutingTable rt;
    memset(&rt, 0, sizeof(rt));
    rt.num_shards = 3;
    rt.use_hash_routing = false; /* Використовуємо Range для ілюстрації SCAN */

    /* Конфігурація трьох діапазонних шардів */
    strcpy(rt.shards[0].range_start, "A");
    strcpy(rt.shards[0].range_end, "H");
    strcpy(rt.shards[0].node_addr, "10.0.0.1:5432");

    strcpy(rt.shards[1].range_start, "I");
    strcpy(rt.shards[1].range_end, "P");
    strcpy(rt.shards[1].node_addr, "10.0.0.2:5432");

    strcpy(rt.shards[2].range_start, "Q");
    strcpy(rt.shards[2].range_end, "Z");
    strcpy(rt.shards[2].node_addr, "10.0.0.3:5432");

    /* Заповнення даними через маршрутизатор */
    router_put(&rt, "Alice", "balance:100");
    router_put(&rt, "Bob", "balance:250");
    router_put(&rt, "Charlie", "balance:80");
    router_put(&rt, "Ivan", "balance:300");
    router_put(&rt, "Maria", "balance:500");
    router_put(&rt, "Roman", "balance:120");
    router_put(&rt, "Taras", "balance:990");
    router_put(&rt, "Zenon", "balance:430");

    /* Точкові запити */
    printf("Точковий роутинг 'Bob' -> Шард %d (%s)\n",
           route_point_query(&rt, "Bob"), rt.shards[route_point_query(&rt, "Bob")].node_addr);
    printf("Точковий роутинг 'Taras' -> Шард %d (%s)\n\n",
           route_point_query(&rt, "Taras"), rt.shards[route_point_query(&rt, "Taras")].node_addr);

    /* Віялове сканування з сортуванням злиттям */
    router_scatter_gather_scan(&rt, "A", "Z", 5, 0);
    router_scatter_gather_scan(&rt, "B", "T", 3, 2);

    return 0;
}
