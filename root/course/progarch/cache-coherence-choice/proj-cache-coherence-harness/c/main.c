#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <stdint.h>

#define MAX_KEY_LEN 64
#define MAX_VAL_LEN 128

typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    uint64_t version;
    bool valid;
} CacheEntry;

typedef struct {
    CacheEntry entries[16];
    pthread_mutex_t lock;
} DistributedCache;

typedef struct {
    char id[MAX_KEY_LEN];
    char address[MAX_VAL_LEN];
    uint64_t version;
} UserRecord;

typedef struct {
    UserRecord records[16];
    pthread_mutex_t lock;
} PrimaryDatabase;

static DistributedCache g_cache;
static PrimaryDatabase g_db;

void cache_init(DistributedCache *cache) {
    pthread_mutex_init(&cache->lock, NULL);
    for (int i = 0; i < 16; i++) {
        cache->entries[i].valid = false;
        cache->entries[i].version = 0;
    }
}

void db_init(PrimaryDatabase *db) {
    pthread_mutex_init(&db->lock, NULL);
    for (int i = 0; i < 16; i++) {
        snprintf(db->records[i].id, MAX_KEY_LEN, "user_%d", i);
        snprintf(db->records[i].address, MAX_VAL_LEN, "Old Address %d", i);
        db->records[i].version = 1;
    }
}

/* 1. Небезпечний подвійний запис (Dual-Write Fail) */
bool unsafe_update_user(const char *user_id, const char *new_addr, bool simulate_network_crash) {
    pthread_mutex_lock(&g_db.lock);
    int idx = -1;
    for (int i = 0; i < 16; i++) {
        if (strcmp(g_db.records[i].id, user_id) == 0) {
            idx = i;
            break;
        }
    }
    if (idx != -1) {
        snprintf(g_db.records[idx].address, MAX_VAL_LEN, "%s", new_addr);
        g_db.records[idx].version++;
    }
    pthread_mutex_unlock(&g_db.lock);

    /* Збій на кроці 2: мережа моргнула до виклику cache_evict */
    if (simulate_network_crash) {
        printf("[Unsafe Dual-Write] DB updated, but Cache eviction CRASHED!\n");
        return false; /* Кеш залишився зомбі */
    }

    pthread_mutex_lock(&g_cache.lock);
    for (int i = 0; i < 16; i++) {
        if (strcmp(g_cache.entries[i].key, user_id) == 0) {
            g_cache.entries[i].valid = false; /* Evict */
        }
    }
    pthread_mutex_unlock(&g_cache.lock);
    return true;
}

/* 2. БЕЗПЕЧНА ІНВАЛІДАЦІЯ: Cache-Aside з версійним бар'єром (Eviction + Version Check) */
bool safe_cache_put_if_newer(const char *key, const char *val, uint64_t version) {
    pthread_mutex_lock(&g_cache.lock);
    int target_idx = -1;
    for (int i = 0; i < 16; i++) {
        if (g_cache.entries[i].valid && strcmp(g_cache.entries[i].key, key) == 0) {
            target_idx = i;
            break;
        }
    }

    if (target_idx != -1) {
        /* Захист від запізнілого запису: ігноруємо, якщо версія в кеші вже новіша */
        if (g_cache.entries[target_idx].version >= version) {
            printf("[Cache-Aside Guard] Stale write rejected! Cache version (%glu) >= Incoming (%glu)\n",
                   (unsigned long)g_cache.entries[target_idx].version, (unsigned long)version);
            pthread_mutex_unlock(&g_cache.lock);
            return false;
        }
    } else {
        /* Шукаємо вільний слот */
        for (int i = 0; i < 16; i++) {
            if (!g_cache.entries[i].valid) {
                target_idx = i;
                break;
            }
        }
    }

    if (target_idx != -1) {
        snprintf(g_cache.entries[target_idx].key, MAX_KEY_LEN, "%s", key);
        snprintf(g_cache.entries[target_idx].value, MAX_VAL_LEN, "%s", val);
        g_cache.entries[target_idx].version = version;
        g_cache.entries[target_idx].valid = true;
        printf("[Cache-Aside] Cache updated key=%s, val=%s, ver=%glu\n", key, val, (unsigned long)version);
    }
    pthread_mutex_unlock(&g_cache.lock);
    return true;
}

void safe_cache_evict(const char *key) {
    pthread_mutex_lock(&g_cache.lock);
    for (int i = 0; i < 16; i++) {
        if (g_cache.entries[i].valid && strcmp(g_cache.entries[i].key, key) == 0) {
            g_cache.entries[i].valid = false;
            printf("[Cache Evict] Key '%s' evicted from cache successfully.\n", key);
        }
    }
    pthread_mutex_unlock(&g_cache.lock);
}

int main(void) {
    cache_init(&g_cache);
    db_init(&g_db);

    printf("=== SCENARIO 1: Unsafe Dual-Write Failure ===\n");
    unsafe_update_user("user_0", "New Kyiv Address", true);

    /* Перевіряємо застряглий зомбі-стан */
    pthread_mutex_lock(&g_db.lock);
    printf("Primary DB user_0 addr: %s (v=%glu)\n", g_db.records[0].address, (unsigned long)g_db.records[0].version);
    pthread_mutex_unlock(&g_db.lock);

    printf("\n=== SCENARIO 2: Cache-Aside Safe Version Eviction ===\n");
    safe_cache_put_if_newer("user_1", "Old Lviv Address", 1);
    /* Видалення ключа при зміні */
    safe_cache_evict("user_1");

    /* Спроба запізнілого запису старої версії v1 після оновлення до v2 */
    safe_cache_put_if_newer("user_1", "Fresh Odesa Address", 2);
    safe_cache_put_if_newer("user_1", "Stale Late Read Address", 1); /* Мусить бути відхилено */

    return 0;
}
