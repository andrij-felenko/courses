static bool ht_delete(HashTable *t, const char *key) {
    size_t mask = t->cap - 1;
    size_t idx  = fnv1a(key) & mask;
    for (size_t i = 0; i < t->cap; ++i) {
        Slot *s = &t->slots[(idx + i) & mask];
        if (s->state == EMPTY)                // впёрлись у порожню → ключа немає
            return false;
        if (s->state == OCCUPIED && strcmp(s->key, key) == 0) {
            free(s->key);
            s->key   = NULL;
            s->state = DELETED;               // НАДГРОБОК, а не EMPTY!
            t->len--;                         // живих записів менше…
            // …але used НЕ чіпаємо: надгробок і далі подовжує проби
            return true;
        }
    }
    return false;
}
