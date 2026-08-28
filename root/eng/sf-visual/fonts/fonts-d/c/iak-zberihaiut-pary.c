typedef struct {
    uint16_t pair;   // (left << 8) | right — ключ пари, спакований у 16 біт
    int8_t   adjust; // поправка до кроку, пікселів (зазвичай від'ємна)
} KernPair;

// Знайти поправку для пари (left, right); 0 — пари нема. Список відсортовано за pair.
int8_t kern(const KernPair *table, int n, uint8_t left, uint8_t right) {
    uint16_t key = ((uint16_t)left << 8) | right;
    int lo = 0, hi = n - 1;
    while (lo <= hi) {                       // двійковий пошук O(log n)
        int mid = (lo + hi) >> 1;
        if (table[mid].pair == key) return table[mid].adjust;
        if (table[mid].pair < key)  lo = mid + 1;
        else                        hi = mid - 1;
    }
    return 0;                                // пари нема — кернінгу немає
}
