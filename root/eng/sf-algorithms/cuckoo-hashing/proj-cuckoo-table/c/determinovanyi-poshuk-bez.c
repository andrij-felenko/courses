bool cuckoo_find(const CuckooMap *map, uint64_t key, uint64_t *out_value) {
    if (!map || map->size == 0) return false;

    /* 1. Перевірка першої таблиці */
    size_t i1 = index1(map, key);
    if (map->t1[i1].occupied && map->t1[i1].key == key) {
        if (out_value) *out_value = map->t1[i1].value;
        return true;
    }

    /* 2. Перевірка другої таблиці */
    size_t i2 = index2(map, key);
    if (map->t2[i2].occupied && map->t2[i2].key == key) {
        if (out_value) *out_value = map->t2[i2].value;
        return true;
    }

    /* 3. Перевірка схованки (фіксовані 4 слоти) */
    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (map->stash[s].occupied && map->stash[s].key == key) {
            if (out_value) *out_value = map->stash[s].value;
            return true;
        }
    }

    return false;
}
