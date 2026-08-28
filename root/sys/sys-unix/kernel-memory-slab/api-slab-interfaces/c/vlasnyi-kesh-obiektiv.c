struct conn_state {
    struct list_head node;
    spinlock_t       lock;
    u64              id;
    u8               payload[96];
};

static struct kmem_cache *conn_cache;

static int __init conn_init(void)
{
    conn_cache = kmem_cache_create("conn_state", sizeof(struct conn_state),
                                   0, SLAB_HWCACHE_ALIGN | SLAB_ACCOUNT, NULL);
    return conn_cache ? 0 : -ENOMEM;
}

static void __exit conn_exit(void)
{
    kmem_cache_destroy(conn_cache);   /* усі об'єкти мають бути вже звільнені */
}

struct conn_state *conn_get(void)
{
    struct conn_state *c = kmem_cache_alloc(conn_cache, GFP_KERNEL | __GFP_ZERO);

    if (!c)
        return NULL;
    INIT_LIST_HEAD(&c->node);
    spin_lock_init(&c->lock);
    return c;
}
