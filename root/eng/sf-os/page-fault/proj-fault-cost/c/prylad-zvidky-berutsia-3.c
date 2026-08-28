static void touch_seq(char *p, size_t len, int write)
{
    unsigned long acc = 0;
    for (size_t i = 0; i < len; i += PGSZ)
        if (write) p[i] = 1;
        else       acc += (unsigned char)p[i];
    sink += acc;                        /* без цього рядка циклу не буде */
}

/* Випадковий порядок готуємо ЗАЗДАЛЕГІДЬ: генератор випадкових чисел
   у виміряному циклі — це вимір генератора, а не пам'яті. */
static size_t *permutation(size_t n)
{
    size_t *idx = malloc(n * sizeof *idx);
    for (size_t i = 0; i < n; i++) idx[i] = i;
    for (size_t i = n - 1; i > 0; i--) {
        size_t j = (size_t)(random() % (long)(i + 1));
        size_t t = idx[i]; idx[i] = idx[j]; idx[j] = t;
    }
    return idx;
}

static void touch_perm(char *p, const size_t *idx, size_t n)
{
    unsigned long acc = 0;
    for (size_t k = 0; k < n; k++) acc += (unsigned char)p[idx[k] * PGSZ];
    sink += acc;
}
