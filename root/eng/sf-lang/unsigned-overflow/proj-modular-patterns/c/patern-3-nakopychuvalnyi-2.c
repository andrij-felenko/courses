// ініціалізація
uint32_t h = FNV_OFFSET_32;

// на кожен новий шматок (можна кликати скільки завгодно разів)
static uint32_t fnv1a_update(uint32_t h, const uint8_t *chunk, size_t n) {
    for (size_t i = 0; i < n; i++) {
        h ^= chunk[i];
        h *= FNV_PRIME_32;
    }
    return h;                          // передаси назад у наступний виклик
}
