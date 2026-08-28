int main(void) {
    HashTable t;
    ht_init(&t, 8);

    put(&t, "cat", 1);
    put(&t, "act", 2);
    put(&t, "dog", 3);
    put(&t, "cat", 42);                        // оновлення наявного ключа

    long v;
    printf("cat = %ld\n", ht_get(&t, "cat", &v) ? v : -1);   // 42
    printf("act = %ld\n", ht_get(&t, "act", &v) ? v : -1);   // 2

    ht_delete(&t, "act");                      // ставить надгробок
    printf("act? %d\n", ht_get(&t, "act", &v));               // 0 — немає
    printf("dog = %ld\n", ht_get(&t, "dog", &v) ? v : -1);   // 3 — досі знаходиться

    char k[16];
    for (int i = 0; i < 100; ++i) {            // 100 вставок → кілька розширень
        sprintf(k, "n%d", i);
        put(&t, k, i);
    }
    printf("len=%zu used=%zu cap=%zu\n", t.len, t.used, t.cap);

    ht_free(&t);
    return 0;
}
