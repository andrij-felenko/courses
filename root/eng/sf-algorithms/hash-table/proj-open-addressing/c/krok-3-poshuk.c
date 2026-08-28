static bool ht_get(const HashTable *t, const char *key, long *out) {
    size_t mask = t->cap - 1;                 // cap — степінь двійки
    size_t idx  = fnv1a(key) & mask;          // згортання = маскування
    for (size_t i = 0; i < t->cap; ++i) {
        Slot *s = &t->slots[(idx + i) & mask];// лінійна проба по колу
        if (s->state == EMPTY)                // порожньо → ключа немає
            return false;
        if (s->state == OCCUPIED && strcmp(s->key, key) == 0) {
            if (out) *out = s->value;
            return true;
        }
        // DELETED або чужий OCCUPIED → переступаємо, проба далі
    }
    return false;                             // оминули всю таблицю — не знайшли
}
