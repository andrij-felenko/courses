static void ht_init(HashTable *t, size_t cap) {
    t->cap  = cap;                          // степінь двійки, напр. 8
    t->len  = t->used = 0;
    t->slots = calloc(cap, sizeof(Slot));   // усі комірки → EMPTY(0), key=NULL
}

static void ht_free(HashTable *t) {
    for (size_t i = 0; i < t->cap; ++i)
        if (t->slots[i].state == OCCUPIED)
            free(t->slots[i].key);          // звільняємо лише живі ключі
    free(t->slots);
    t->slots = NULL; t->cap = t->len = t->used = 0;
}
