// Сумарна довжина списку. Простір адрес — будь-який (адреси не чіпаємо).
// false ⇒ сума не влазить у size_t; *out не змінено. O(n).
bool sg_total(const struct sg_list *sg, size_t *out) {
    size_t s = 0;
    for (int i = 0; i < sg->n; i++) {
        if (s > SIZE_MAX - sg->seg[i].len) return false;   // перевірка ДО додавання
        s += sg->seg[i].len;
    }
    *out = s;
    return true;
}
