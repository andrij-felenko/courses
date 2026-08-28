// Токен кладемо в КОЖЕН запис; сховище відкидає застарілі саме на записі.
typedef struct {
    uint64_t highest_seen;   // найбільший токен, який сховище вже приймало
} FencedStore;

void store_init(FencedStore *s) { s->highest_seen = 0; }

// Повертає true, якщо запис прийнято. Це — ЄДИНЕ місце істини про те,
// хто зараз має право писати. Тут гине розкол мозку.
bool store_write(FencedStore *s, uint64_t token, const void *data, int len) {
    if (token < s->highest_seen) {
        // запис від відсталого «головного» — мовчки НЕ псуємо дані
        fprintf(stderr, "fenced: токен %llu < %llu, запис відкинуто\n",
                (unsigned long long)token, (unsigned long long)s->highest_seen);
        return false;
    }
    s->highest_seen = token;         // монотонно піднімаємо планку
    // ... власне запис data[0..len) ...
    (void)data; (void)len;
    return true;
}
