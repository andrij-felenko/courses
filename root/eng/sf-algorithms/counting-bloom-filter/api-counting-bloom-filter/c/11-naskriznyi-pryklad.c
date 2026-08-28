#include <stdio.h>
#include <string.h>

void demo_cbf_lifecycle(void) {
    /* 1. Розрахунок параметрів для 100 000 ключів із похибкою 1% */
    size_t cap = cbf_optimal_capacity(100000, 0.01);
    uint32_t k = cbf_optimal_hashes(cap, 100000);

    /* 2. Створення фільтра */
    CountingBloomFilter *filter = cbf_create(cap, k);
    if (!filter) return;

    /* 3. Додавання ключів */
    const char *key1 = "session_token_xyz_998";
    cbf_insert(filter, key1, strlen(key1));

    /* 4. Перевірка наявності */
    if (cbf_contains(filter, key1, strlen(key1))) {
        printf("Ключ знайдено!\n");
    }

    /* 5. Видалення ключа */
    cbf_remove(filter, key1, strlen(key1));

    /* 6. Звільнення пам'яті */
    cbf_destroy(filter);
}
