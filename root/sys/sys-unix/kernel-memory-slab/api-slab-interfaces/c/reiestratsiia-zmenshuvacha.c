static struct list_lru  conn_lru;
static struct shrinker *conn_shrinker;

static unsigned long conn_count(struct shrinker *sh, struct shrink_control *sc)
{
    unsigned long n = list_lru_shrink_count(&conn_lru, sc);

    return n ? n : SHRINK_EMPTY;
}

static enum lru_status conn_isolate(struct list_head *item,
                                    struct list_lru_one *lru,
                                    spinlock_t *lock, void *arg)
{
    struct conn_state *c = container_of(item, struct conn_state, node);
    struct list_head *freeable = arg;

    if (!spin_trylock(&c->lock))
        return LRU_SKIP;               /* зайнято — не чекаємо, беремо наступний */
    list_lru_isolate_move(lru, item, freeable);
    spin_unlock(&c->lock);
    return LRU_REMOVED;
}

static unsigned long conn_scan(struct shrinker *sh, struct shrink_control *sc)
{
    struct conn_state *c, *tmp;
    LIST_HEAD(freeable);
    unsigned long freed;

    if (!(sc->gfp_mask & __GFP_FS))
        return SHRINK_STOP;            /* нас покликала сама файлова система */

    freed = list_lru_shrink_walk(&conn_lru, sc, conn_isolate, &freeable);

    list_for_each_entry_safe(c, tmp, &freeable, node) {
        list_del(&c->node);
        kmem_cache_free(conn_cache, c);
    }
    return freed;
}

static int conn_shrinker_init(void)
{
    conn_shrinker = shrinker_alloc(SHRINKER_NUMA_AWARE | SHRINKER_MEMCG_AWARE,
                                   "conn-state");
    if (!conn_shrinker)
        return -ENOMEM;

    if (list_lru_init_memcg(&conn_lru, conn_shrinker)) {
        shrinker_free(conn_shrinker);  /* до реєстрації — просто звільнити */
        return -ENOMEM;
    }

    conn_shrinker->count_objects = conn_count;
    conn_shrinker->scan_objects  = conn_scan;
    conn_shrinker->seeks         = DEFAULT_SEEKS;
    conn_shrinker->private_data  = &conn_lru;

    shrinker_register(conn_shrinker);
    return 0;
}
