int main(void) {
    CuckooMap *map = cuckoo_create(16);
    if (!map) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    const uint64_t N = 10000;
    for (uint64_t k = 1; k <= N; ++k) {
        if (!cuckoo_insert(map, k, k * 10)) {
            fprintf(stderr, "Збій вставки ключа %llu\n", (unsigned long long)k);
            cuckoo_destroy(map);
            return 1;
        }
    }

    /* Перевірка наявності */
    for (uint64_t k = 1; k <= N; ++k) {
        uint64_t val = 0;
        if (!cuckoo_find(map, k, &val) || val != k * 10) {
            fprintf(stderr, "Збій пошуку ключа %llu\n", (unsigned long long)k);
            cuckoo_destroy(map);
            return 1;
        }
    }

    /* Перевірка видалення половини елементів */
    for (uint64_t k = 1; k <= N; k += 2) {
        cuckoo_erase(map, k);
    }

    for (uint64_t k = 1; k <= N; ++k) {
        uint64_t val = 0;
        bool found = cuckoo_find(map, k, &val);
        if (k % 2 != 0 && found) {
            fprintf(stderr, "Помилка: видалений ключ %llu знайдено\n", (unsigned long long)k);
            cuckoo_destroy(map);
            return 1;
        }
        if (k % 2 == 0 && (!found || val != k * 10)) {
            fprintf(stderr, "Помилка: збережений ключ %llu не знайдено\n", (unsigned long long)k);
            cuckoo_destroy(map);
            return 1;
        }
    }

    printf("Усі тести хешування зозулею пройдено успішно. Розмір: %zu, Місткість: %zu\n",
           map->size, map->capacity * 2);
    cuckoo_destroy(map);
    return 0;
}
