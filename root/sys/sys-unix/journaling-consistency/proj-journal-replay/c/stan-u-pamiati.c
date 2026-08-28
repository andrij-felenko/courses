typedef struct { uint8_t *key; uint32_t klen; uint8_t *val; uint32_t vlen; } Entry;

typedef struct {
    int      fd;
    int      durable;    /* 1 — fsync на кожен put */
    uint64_t next_seq;
    off_t    end;        /* зсув після останнього справного запису */
    Entry   *tab;
    size_t   n, cap;
} KV;

static Entry *find(KV *kv, const uint8_t *key, uint32_t klen) {
    for (size_t i = 0; i < kv->n; i++)
        if (kv->tab[i].klen == klen && memcmp(kv->tab[i].key, key, klen) == 0)
            return &kv->tab[i];
    return NULL;
}

static int apply(KV *kv, uint8_t op, const uint8_t *key, uint32_t klen,
                 const uint8_t *val, uint32_t vlen) {
    Entry *e = find(kv, key, klen);

    if (op == OP_DEL) {
        if (e) { free(e->key); free(e->val); *e = kv->tab[--kv->n]; }
        return 0;
    }
    if (!e) {
        if (kv->n == kv->cap) {
            size_t cap = kv->cap ? kv->cap * 2 : 64;
            Entry *t = realloc(kv->tab, cap * sizeof *t);
            if (!t) return -1;
            kv->tab = t; kv->cap = cap;
        }
        uint8_t *k = malloc(klen ? klen : 1);
        if (!k) return -1;
        if (klen) memcpy(k, key, klen);
        e = &kv->tab[kv->n++];
        e->key = k; e->klen = klen; e->val = NULL; e->vlen = 0;
    }
    uint8_t *v = malloc(vlen ? vlen : 1);
    if (!v) return -1;
    if (vlen) memcpy(v, val, vlen);
    free(e->val);
    e->val = v; e->vlen = vlen;
    return 0;
}
