static bool cuckoo_insert_entry(CuckooMap *map, CuckooEntry curr);

static bool cuckoo_rehash(CuckooMap *map, size_t new_capacity) {
    CuckooEntry *old_t1 = map->t1;
    CuckooEntry *old_t2 = map->t2;
    CuckooEntry old_stash[STASH_CAPACITY];
    memcpy(old_stash, map->stash, sizeof(old_stash));
    size_t old_cap = map->capacity;

    map->t1 = (CuckooEntry *)calloc(new_capacity, sizeof(CuckooEntry));
    map->t2 = (CuckooEntry *)calloc(new_capacity, sizeof(CuckooEntry));
    if (!map->t1 || !map->t2) {
        free(map->t1);
        free(map->t2);
        map->t1 = old_t1;
        map->t2 = old_t2;
        return false;
    }
    memset(map->stash, 0, sizeof(map->stash));
    map->capacity = new_capacity;
    map->size = 0;
    map->seed1 += 0x9E3779B9ULL;
    map->seed2 += 0xC6A4A793ULL;

    /* Перевставка всіх елементів з попередніх масивів */
    for (size_t i = 0; i < old_cap; ++i) {
        if (old_t1[i].occupied) cuckoo_insert_entry(map, old_t1[i]);
        if (old_t2[i].occupied) cuckoo_insert_entry(map, old_t2[i]);
    }
    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (old_stash[s].occupied) cuckoo_insert_entry(map, old_stash[s]);
    }

    free(old_t1);
    free(old_t2);
    return true;
}

static bool cuckoo_insert_entry(CuckooMap *map, CuckooEntry curr) {
    size_t max_steps = map->capacity * MAX_DISPLACEMENTS_FACTOR;

    for (size_t step = 0; step < max_steps; ++step) {
        /* Спроба помістити в T1 */
        size_t i1 = index1(map, curr.key);
        if (!map->t1[i1].occupied) {
            map->t1[i1] = curr;
            map->size++;
            return true;
        }

        /* Витіснення з T1 */
        CuckooEntry victim1 = map->t1[i1];
        map->t1[i1] = curr;
        curr = victim1;

        /* Спроба помістити витісненого в T2 */
        size_t i2 = index2(map, curr.key);
        if (!map->t2[i2].occupied) {
            map->t2[i2] = curr;
            map->size++;
            return true;
        }

        /* Витіснення з T2 */
        CuckooEntry victim2 = map->t2[i2];
        map->t2[i2] = curr;
        curr = victim2;
    }

    /* Ліміт витіснень вичерпано: пробуємо покласти в схованку */
    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (!map->stash[s].occupied) {
            map->stash[s] = curr;
            map->size++;
            return true;
        }
    }

    /* Схованка заповнена: потрібне перехешування */
    if (!cuckoo_rehash(map, map->capacity * 2)) {
        return false;
    }
    return cuckoo_insert_entry(map, curr);
}

bool cuckoo_insert(CuckooMap *map, uint64_t key, uint64_t value) {
    if (!map) return false;

    /* Якщо ключ уже існує — оновлюємо значення */
    size_t i1 = index1(map, key);
    if (map->t1[i1].occupied && map->t1[i1].key == key) {
        map->t1[i1].value = value;
        return true;
    }
    size_t i2 = index2(map, key);
    if (map->t2[i2].occupied && map->t2[i2].key == key) {
        map->t2[i2].value = value;
        return true;
    }
    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (map->stash[s].occupied && map->stash[s].key == key) {
            map->stash[s].value = value;
            return true;
        }
    }

    CuckooEntry entry = { .key = key, .value = value, .occupied = true };
    return cuckoo_insert_entry(map, entry);
}
