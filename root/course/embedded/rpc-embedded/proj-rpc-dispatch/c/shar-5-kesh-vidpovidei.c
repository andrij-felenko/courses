#define CACHE_SIZE  4          // памʼять на останні 4 виконані запити

typedef struct {
    bool        used;          // запис зайнятий?
    uint8_t     id;            // ID виконаного запиту
    rpc_resp_t  resp;          // готова відповідь на нього
} cache_slot_t;

static cache_slot_t g_cache[CACHE_SIZE];
static size_t       g_cache_next = 0;   // куди писати наступну (по колу)

// Шукаємо в кеші готову відповідь за ID. NULL, якщо такого ще не бачили.
static const rpc_resp_t *cache_find(uint8_t id) {
    for (size_t i = 0; i < CACHE_SIZE; i++)
        if (g_cache[i].used && g_cache[i].id == id)
            return &g_cache[i].resp;
    return NULL;
}

// Запамʼятати відповідь (затираємо найстаріший запис по колу).
static void cache_store(uint8_t id, const rpc_resp_t *resp) {
    g_cache[g_cache_next].used = true;
    g_cache[g_cache_next].id   = id;
    g_cache[g_cache_next].resp = *resp;
    g_cache_next = (g_cache_next + 1) % CACHE_SIZE;
}
