#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

#define MAX_KEY_LEN 128
#define MAX_VAL_LEN 4096
#define HASH_TABLE_SIZE 1024

/* Запис у кеші з таймером свіжості (TTL) */
typedef struct CacheEntry {
    char key[MAX_KEY_LEN];
    char data[MAX_VAL_LEN];
    size_t data_len;
    time_t expires_at;
    struct CacheEntry* next;
} CacheEntry;

/* Стан активного вихідного запиту до Origin (In-flight request) */
typedef struct InflightRequest {
    char key[MAX_KEY_LEN];
    int is_done;
    int error_code;
    pthread_cond_t cond;
    struct InflightRequest* next;
} InflightRequest;

/* Структура кешувального рушія */
typedef struct {
    CacheEntry* cache_buckets[HASH_TABLE_SIZE];
    InflightRequest* inflight_buckets[HASH_TABLE_SIZE];
    pthread_mutex_t mutex;
} EdgeCache;

/* Хеш-функція djb2 для ключів URI */
static unsigned long hash_key(const char* str) {
    unsigned long hash = 5381;
    int c;
    while ((c = (unsigned char)*str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_TABLE_SIZE;
}

void edge_cache_init(EdgeCache* ec) {
    memset(ec->cache_buckets, 0, sizeof(ec->cache_buckets));
    memset(ec->inflight_buckets, 0, sizeof(ec->inflight_buckets));
    pthread_mutex_init(&ec->mutex, NULL);
}

/* Симуляція мережевого запиту до сервера-джерела (Origin) */
static int fetch_from_origin(const char* key, char* out_buf, size_t* out_len) {
    /* Симуляція затримки магістрального каналу 100 мс */
    usleep(100000);
    int written = snprintf(out_buf, MAX_VAL_LEN, "Payload for [%s] generated at %ld", key, time(NULL));
    if (written < 0 || written >= MAX_VAL_LEN) {
        return -1;
    }
    *out_len = (size_t)written;
    return 0;
}

/* Отримання даних з кешу або завантаження через Single-Flight */
int edge_cache_get(EdgeCache* ec, const char* key, int ttl_seconds, char* out_buf, size_t* out_len) {
    unsigned long h = hash_key(key);
    time_t now = time(NULL);

    pthread_mutex_lock(&ec->mutex);

    /* 1. Перевірка наявності валідного запису в кеші */
    CacheEntry* ce = ec->cache_buckets[h];
    while (ce) {
        if (strcmp(ce->key, key) == 0) {
            if (ce->expires_at > now) {
                /* Cache HIT */
                memcpy(out_buf, ce->data, ce->data_len);
                *out_len = ce->data_len;
                pthread_mutex_unlock(&ec->mutex);
                return 0;
            }
            break; /* Запис застарів, потрібне оновлення */
        }
        ce = ce->next;
    }

    /* 2. Перевірка, чи запит за цим ключем уже виконується іншим потоком */
    InflightRequest* inf = ec->inflight_buckets[h];
    while (inf) {
        if (strcmp(inf->key, key) == 0) {
            break;
        }
        inf = inf->next;
    }

    if (inf) {
        /* Запит вже в польоті: блокуємося та очікуємо завершення */
        while (!inf->is_done) {
            pthread_cond_wait(&inf->cond, &ec->mutex);
        }
        
        /* Після пробудження читаємо збережений кеш */
        ce = ec->cache_buckets[h];
        while (ce) {
            if (strcmp(ce->key, key) == 0 && ce->expires_at > now) {
                memcpy(out_buf, ce->data, ce->data_len);
                *out_len = ce->data_len;
                pthread_mutex_unlock(&ec->mutex);
                return 0;
            }
            ce = ce->next;
        }
        pthread_mutex_unlock(&ec->mutex);
        return -1; /* Помилка завантаження першим потоком */
    }

    /* 3. Ми — перший потік: створюємо InflightRequest */
    InflightRequest new_inf;
    strncpy(new_inf.key, key, MAX_KEY_LEN - 1);
    new_inf.key[MAX_KEY_LEN - 1] = '\0';
    new_inf.is_done = 0;
    new_inf.error_code = 0;
    pthread_cond_init(&new_inf.cond, NULL);

    new_inf.next = ec->inflight_buckets[h];
    ec->inflight_buckets[h] = &new_inf;

    /* Звільняємо блокування на час мережевого запиту до Origin */
    pthread_mutex_unlock(&ec->mutex);

    char origin_data[MAX_VAL_LEN];
    size_t origin_len = 0;
    int res = fetch_from_origin(key, origin_data, &origin_len);

    /* 4. Завершення виклику: збереження в кеш та сповіщення очікуючих потоків */
    pthread_mutex_lock(&ec->mutex);

    if (res == 0) {
        /* Збереження або оновлення в кеші */
        ce = ec->cache_buckets[h];
        while (ce && strcmp(ce->key, key) != 0) {
            ce = ce->next;
        }
        if (!ce) {
            ce = (CacheEntry*)malloc(sizeof(CacheEntry));
            strncpy(ce->key, key, MAX_KEY_LEN - 1);
            ce->key[MAX_KEY_LEN - 1] = '\0';
            ce->next = ec->cache_buckets[h];
            ec->cache_buckets[h] = ce;
        }
        memcpy(ce->data, origin_data, origin_len);
        ce->data_len = origin_len;
        ce->expires_at = time(NULL) + ttl_seconds;

        memcpy(out_buf, origin_data, origin_len);
        *out_len = origin_len;
    }

    /* Видалення з inflight_buckets */
    InflightRequest** curr = &ec->inflight_buckets[h];
    while (*curr) {
        if (*curr == &new_inf) {
            *curr = new_inf.next;
            break;
        }
        curr = &(*curr)->next;
    }

    new_inf.is_done = 1;
    new_inf.error_code = res;
    pthread_cond_broadcast(&new_inf.cond);
    pthread_mutex_unlock(&ec->mutex);

    pthread_cond_destroy(&new_inf.cond);
    return res;
}
