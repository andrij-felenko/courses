// Шукає найдовший збіг для src[pos..] у вікні src[pos-WINDOW .. pos-1].
// Повертає довжину; *best_off — зсув назад до знайденого збігу.
static size_t find_match(const uint8_t *src, size_t n, size_t pos, size_t *best_off) {
    size_t best_len = 0;
    *best_off = 0;

    // початок вікна пошуку: не далі ніж WINDOW назад і не лівіше за початок даних
    size_t start = (pos > WINDOW) ? pos - WINDOW : 0;

    for (size_t cand = start; cand < pos; cand++) {
        // тягнемо збіг від cand і від pos, поки байти однакові
        size_t len = 0;
        while (len < MAX_LEN &&
               pos + len < n &&
               src[cand + len] == src[pos + len]) {
            len++;
        }
        if (len > best_len) {            // знайшли довший — запам'ятовуємо
            best_len = len;
            *best_off = pos - cand;      // зсув назад
        }
    }
    return best_len;
}
