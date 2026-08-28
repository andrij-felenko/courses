bool cuckoo_erase(CuckooMap *map, uint64_t key) {
    if (!map || map->size == 0) return false;

    size_t i1 = index1(map, key);
    if (map->t1[i1].occupied && map->t1[i1].key == key) {
        map->t1[i1].occupied = false;
        map->size--;
        return true;
    }

    size_t i2 = index2(map, key);
    if (map->t2[i2].occupied && map->t2[i2].key == key) {
        map->t2[i2].occupied = false;
        map->size--;
        return true;
    }

    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (map->stash[s].occupied && map->stash[s].key == key) {
            map->stash[s].occupied = false;
            map->size--;
            return true;
        }
    }

    return false;
}
