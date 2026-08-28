#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_KEY_LEN 256
#define MAX_VAL_LEN 1024
#define CMS_DEPTH 4
#define CMS_WIDTH 2048
#define HOT_THRESHOLD 50
#define SALT_FACTOR 4
#define L1_CAPACITY 64

/* Швидкий некриптографічний 64-бітний хеш MurmurHash3 */
static uint64_t murmurhash3_64(const void* key, size_t len, uint32_t seed) {
    const uint8_t* data = (const uint8_t*)key;
    const size_t nblocks = len / 8;
    uint64_t h = seed ^ (len * 0xc6a4a7935bd1e995ULL);
    const uint64_t m = 0xc6a4a7935bd1e995ULL;
    const int r = 47;

    const uint64_t* blocks = (const uint64_t*)data;
    for (size_t i = 0; i < nblocks; i++) {
        uint64_t k = blocks[i];
        k *= m;
        k ^= k >> r;
        k *= m;
        h ^= k;
        h *= m;
    }

    const uint8_t* tail = (const uint8_t*)(data + nblocks * 8);
    uint64_t k = 0;
    switch (len & 7) {
        case 7: k ^= ((uint64_t)tail[6]) << 48;
        case 6: k ^= ((uint64_t)tail[5]) << 40;
        case 5: k ^= ((uint64_t)tail[4]) << 32;
        case 4: k ^= ((uint64_t)tail[3]) << 24;
        case 3: k ^= ((uint64_t)tail[2]) << 16;
        case 2: k ^= ((uint64_t)tail[1]) << 8;
        case 1: k ^= ((uint64_t)tail[0]);
                k *= m; k ^= k >> r; k *= m; h ^= k;
    };

    h ^= h >> r;
    h *= m;
    h ^= h >> r;
    return h;
}

/* 1. Канонічний побудовник ключів */
typedef struct {
    char service[32];
    char tenant[32];
    char entity[32];
    char id[32];
    char slot_tag[32];
    uint32_t schema_version;
} KeySpec;

bool build_canonical_key(const KeySpec* spec, const char* query_params, char* out_buf, size_t out_max) {
    if (!spec || !out_buf || out_max < 32) return false;

    char hash_suffix[32] = "";
    if (query_params && strlen(query_params) > 0) {
        uint64_t h = murmurhash3_64(query_params, strlen(query_params), 0x9747b28c);
        snprintf(hash_suffix, sizeof(hash_suffix), ":%016llx", (unsigned long long)h);
    }

    char tag_part[40] = "";
    if (strlen(spec->slot_tag) > 0) {
        snprintf(tag_part, sizeof(tag_part), ":{%s}", spec->slot_tag);
    }

    int written = snprintf(out_buf, out_max, "%s:%s:%s:%s%s:v%u%s",
                           spec->service, spec->tenant, spec->entity,
                           spec->id, tag_part, spec->schema_version, hash_suffix);

    return (written > 0 && (size_t)written < out_max);
}

/* 2. Потоковий детектор гарячих точок Count-Min Sketch */
typedef struct {
    uint32_t table[CMS_DEPTH][CMS_WIDTH];
    uint32_t seeds[CMS_DEPTH];
    uint32_t total_count;
} CountMinSketch;

void cms_init(CountMinSketch* cms) {
    memset(cms->table, 0, sizeof(cms->table));
    cms->seeds[0] = 0x1337beef;
    cms->seeds[1] = 0xdeadc0de;
    cms->seeds[2] = 0xcafebabe;
    cms->seeds[3] = 0x8badf00d;
    cms->total_count = 0;
}

void cms_record(CountMinSketch* cms, const char* key) {
    size_t len = strlen(key);
    for (int i = 0; i < CMS_DEPTH; i++) {
        uint64_t hash = murmurhash3_64(key, len, cms->seeds[i]);
        uint32_t col = (uint32_t)(hash % CMS_WIDTH);
        if (cms->table[i][col] < UINT32_MAX) {
            cms->table[i][col]++;
        }
    }
    cms->total_count++;
}

uint32_t cms_estimate(const CountMinSketch* cms, const char* key) {
    size_t len = strlen(key);
    uint32_t min_count = UINT32_MAX;
    for (int i = 0; i < CMS_DEPTH; i++) {
        uint64_t hash = murmurhash3_64(key, len, cms->seeds[i]);
        uint32_t col = (uint32_t)(hash % CMS_WIDTH);
        if (cms->table[i][col] < min_count) {
            min_count = cms->table[i][col];
        }
    }
    return min_count;
}

void cms_decay(CountMinSketch* cms) {
    for (int i = 0; i < CMS_DEPTH; i++) {
        for (int j = 0; j < CMS_WIDTH; j++) {
            cms->table[i][j] /= 2;
        }
    }
    cms->total_count /= 2;
}

/* 3. Дворівневий кеш-менеджер із солінням (Key Salting) */
typedef struct {
    char key[MAX_KEY_LEN];
    char val[MAX_VAL_LEN];
    time_t expires_at;
} L1Entry;

typedef struct {
    L1Entry l1[L1_CAPACITY];
    size_t l1_count;
    CountMinSketch detector;
} AdaptiveCache;

void cache_init(AdaptiveCache* c) {
    c->l1_count = 0;
    cms_init(&c->detector);
    srand((unsigned int)time(NULL));
}

const char* l1_get(AdaptiveCache* c, const char* key) {
    time_t now = time(NULL);
    for (size_t i = 0; i < c->l1_count; i++) {
        if (strcmp(c->l1[i].key, key) == 0) {
            if (c->l1[i].expires_at >= now) {
                return c->l1[i].val;
            }
            /* Сплив термін дії */
            c->l1[i] = c->l1[c->l1_count - 1];
            c->l1_count--;
            return NULL;
        }
    }
    return NULL;
}

void l1_put(AdaptiveCache* c, const char* key, const char* val, int ttl_sec) {
    time_t now = time(NULL);
    for (size_t i = 0; i < c->l1_count; i++) {
        if (strcmp(c->l1[i].key, key) == 0) {
            strncpy(c->l1[i].val, val, MAX_VAL_LEN - 1);
            c->l1[i].expires_at = now + ttl_sec;
            return;
        }
    }
    if (c->l1_count < L1_CAPACITY) {
        strncpy(c->l1[c->l1_count].key, key, MAX_KEY_LEN - 1);
        strncpy(c->l1[c->l1_count].val, val, MAX_VAL_LEN - 1);
        c->l1[c->l1_count].expires_at = now + ttl_sec;
        c->l1_count++;
    }
}

/* Симуляція віддаленого L2-кластера з підрахунком звернень до шарду */
static int cluster_shard_hits[16] = {0};

void l2_mock_set(const char* key, const char* val) {
    (void)key; (void)val;
}

void l2_mock_get(const char* key, char* out_val, size_t out_max) {
    uint64_t h = murmurhash3_64(key, strlen(key), 0x55aa55aa);
    int shard = (int)(h % 16);
    cluster_shard_hits[shard]++;
    snprintf(out_val, out_max, "DataFor(%s)", key);
}

/* Читання через адаптивний контролер */
bool adaptive_cache_get(AdaptiveCache* c, const char* base_key, char* out_buf, size_t out_max) {
    /* Крок 1: Перевірка L1 In-Process */
    const char* l1_val = l1_get(c, base_key);
    if (l1_val) {
        strncpy(out_buf, l1_val, out_max - 1);
        return true;
    }

    /* Крок 2: Фіксація звернення в детекторі аномалій */
    cms_record(&c->detector, base_key);
    uint32_t frequency = cms_estimate(&c->detector, base_key);

    /* Крок 3: Якщо ключ став гарячим — обираємо солений підключ для L2 */
    char fetch_key[MAX_KEY_LEN];
    if (frequency >= HOT_THRESHOLD) {
        int salt = rand() % SALT_FACTOR;
        snprintf(fetch_key, sizeof(fetch_key), "%s#%d", base_key, salt);
        
        /* Зчитуємо з L2 та промоутимо в локальний L1 на короткий час */
        l2_mock_get(fetch_key, out_buf, out_max);
        l1_put(c, base_key, out_buf, 3);
        return true;
    }

    /* Холодний/звичайний ключ: пряме читання базового ключа з L2 */
    l2_mock_get(base_key, out_buf, out_max);
    return true;
}

int main(void) {
    KeySpec spec = {
        .service = "catalog",
        .tenant = "client_ua",
        .entity = "product",
        .id = "9901",
        .slot_tag = "prod_9901",
        .schema_version = 2
    };

    char key[MAX_KEY_LEN];
    build_canonical_key(&spec, "category=electronics&sort=asc", key, sizeof(key));
    printf("Згенеровано канонічний ключ:\n  %s\n\n", key);

    AdaptiveCache cache;
    cache_init(&cache);

    printf("Симуляція 200 запитів до гарячого ключа...\n");
    char result[MAX_VAL_LEN];
    for (int i = 0; i < 200; i++) {
        adaptive_cache_get(&cache, key, result, sizeof(result));
    }

    printf("\nРозподіл звернень по шардах кластера L2:\n");
    for (int s = 0; s < 16; s++) {
        if (cluster_shard_hits[s] > 0) {
            printf("  Шард %2d: %d звернень\n", s, cluster_shard_hits[s]);
        }
    }
    printf("Частотна оцінка Count-Min Sketch: %u\n", cms_estimate(&cache.detector, key));
    return 0;
}
