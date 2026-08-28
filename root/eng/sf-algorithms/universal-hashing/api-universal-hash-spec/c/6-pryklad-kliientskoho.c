#include <stdio.h>
#include <stdlib.h>

void client_example_c(void) {
    uh_config_t cfg = {
        .family_type = UH_FAMILY_MULTIPLY_SHIFT,
        .num_buckets = 2048,
        .use_custom_seed = false
    };

    uh_context_t *hasher = NULL;
    uh_status_t status = uh_create(&hasher, &cfg);
    if (status != UH_SUCCESS) {
        fprintf(stderr, "Помилка створення хешера: %d\n", status);
        return;
    }

    uint64_t key = 0xDEADBEEFCAFEBABEULL;
    uint64_t hash_val = 0;
    uh_hash_uint64(hasher, key, &hash_val);

    printf("Ключ 0x%llX -> Хеш-індекс: %llu\n", key, hash_val);

    uh_destroy(hasher);
}
