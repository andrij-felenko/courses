#include <stddef.h>

/* Реентрабельне сортування у стилі GNU (context першим аргументом компаратора) */
void insertion_sort_r(
    void *base,
    size_t nel,
    size_t width,
    int (*compar)(const void *, const void *, void *),
    void *arg
);

/* Безпечний інтерфейс за стандартом C11 Annex K (context останнім аргументом) */
int insertion_sort_s(
    void *base,
    size_t nel,
    size_t width,
    int (*compar)(const void *, const void *, void *),
    void *context
);
