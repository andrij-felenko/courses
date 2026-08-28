typedef struct {
    size_t in_use;     // зайнято блоків зараз
    size_t peak;       // історичний максимум зайнятого
} pool_stats_t;

static pool_stats_t stats;

void pool_init(void) {
    free_list = NULL;
    memset(used_map, 0, sizeof(used_map));
    stats.in_use = 0;
    stats.peak   = 0;
    for (size_t i = POOL_BLOCKS; i-- > 0; ) {
        void *blk = pool_mem[i];
        *(void **)blk = free_list;
        free_list = blk;
    }
}

void *pool_alloc(void) {
    if (free_list == NULL) {
        return NULL;                       // пул вичерпано — чесно кажемо "ні"
    }
    void *blk = free_list;
    free_list = *(void **)blk;             // знімаємо голову ланцюжка

    bit_set(blk_index(blk));               // позначаємо блок зайнятим
    if (++stats.in_use > stats.peak) {
        stats.peak = stats.in_use;         // оновлюємо пік
    }
    return blk;
}

// Повертає true, якщо блок коректно звільнено; false — якщо повернення хибне
// (чужий покажчик, не на межу блоку, або вже вільний блок).
bool pool_free(void *blk) {
    if (blk == NULL) {
        return true;                       // free(NULL) — дозволено, нічого не робимо
    }
    if (!pool_owns(blk)) {
        return false;                      // це не наш блок або не початок блоку
    }
    size_t i = blk_index(blk);
    if (!bit_get(i)) {
        return false;                      // блок і так вільний → подвійне повернення
    }
    bit_clr(i);                            // позначаємо вільним
    *(void **)blk = free_list;             // вплітаємо в ланцюжок
    free_list = blk;
    stats.in_use--;
    return true;
}
