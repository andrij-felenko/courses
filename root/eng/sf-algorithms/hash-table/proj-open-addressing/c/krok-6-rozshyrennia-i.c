// вставка у СВІЖУ таблицю: без надгробків, без дублікатів; ключ уже наш
static void insert_raw(HashTable *t, char *key, long value) {
    size_t mask = t->cap - 1;
    size_t idx  = fnv1a(key) & mask;
    for (size_t i = 0; ; ++i) {               // порожня комірка тут ГАРАНТОВАНО є
        Slot *s = &t->slots[(idx + i) & mask];
        if (s->state == EMPTY) {
            s->key = key; s->value = value; s->state = OCCUPIED;
            t->len++; t->used++;
            return;
        }
    }
}

static void resize(HashTable *t, size_t new_cap) {
    Slot  *old     = t->slots;
    size_t old_cap = t->cap;

    t->slots = calloc(new_cap, sizeof(Slot)); // нові комірки — усі EMPTY
    t->cap   = new_cap;
    t->len   = t->used = 0;                    // порахуємо заново під час переносу

    for (size_t i = 0; i < old_cap; ++i)
        if (old[i].state == OCCUPIED)          // ЛИШЕ живі — надгробки зникають
            insert_raw(t, old[i].key, old[i].value);  // переносимо вказівник ключа
    free(old);                                 // ключі перенесено; звільняємо тільки масив
}
