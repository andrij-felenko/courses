#include <string.h>

// Хеш-функція FNV-1a для підрядків
static uint64_t fnv1a_hash(const char *str, size_t len) {
    uint64_t hash = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint64_t)(unsigned char)str[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

// Допоміжна функція порівняння для qsort
static int compare_u64(const void *a, const void *b) {
    uint64_t arg1 = *(const uint64_t *)a;
    uint64_t arg2 = *(const uint64_t *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

// Побудова унікального відсортованого масиву хешів k-грам мовою C
size_t create_shingles_c(const char *text, size_t k, uint64_t **out_shingles) {
    size_t text_len = strlen(text);
    if (text_len < k) {
        *out_shingles = NULL;
        return 0;
    }

    size_t count = text_len - k + 1;
    uint64_t *raw = (uint64_t *)malloc(count * sizeof(uint64_t));
    if (!raw) return 0;

    for (size_t i = 0; i < count; ++i) {
        raw[i] = fnv1a_hash(text + i, k);
    }

    qsort(raw, count, sizeof(uint64_t), compare_u64);

    // Дедублікація на місці
    size_t unique_cnt = 0;
    for (size_t i = 0; i < count; ++i) {
        if (i == 0 || raw[i] != raw[i - 1]) {
            raw[unique_cnt++] = raw[i];
        }
    }

    *out_shingles = raw;
    return unique_cnt;
}
