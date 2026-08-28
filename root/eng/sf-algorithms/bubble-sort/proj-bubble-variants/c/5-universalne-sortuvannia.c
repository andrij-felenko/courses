#include <string.h>
#include <stdlib.h>

static void generic_swap(char *a, char *b, size_t size) {
    char buffer[256];
    if (size <= sizeof(buffer)) {
        memcpy(buffer, a, size);
        memcpy(a, b, size);
        memcpy(b, buffer, size);
    } else {
        char *heap_buf = (char *)malloc(size);
        if (heap_buf) {
            memcpy(heap_buf, a, size);
            memcpy(a, b, size);
            memcpy(b, heap_buf, size);
            free(heap_buf);
        }
    }
}

void bubble_sort_generic(void *base, size_t num, size_t size,
                         int (*cmp)(const void *, const void *)) {
    if (num < 2 || size == 0) return;
    char *bytes = (char *)base;
    size_t limit = num - 1;

    while (limit > 0) {
        size_t new_limit = 0;
        for (size_t j = 0; j < limit; ++j) {
            char *elem_a = bytes + j * size;
            char *elem_b = bytes + (j + 1) * size;
            if (cmp(elem_a, elem_b) > 0) {
                generic_swap(elem_a, elem_b, size);
                new_limit = j;
            }
        }
        limit = new_limit;
    }
}
