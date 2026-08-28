/* C11 + POSIX.1-2008: Потікобезпечне сортування через strxfrm_l */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>

typedef struct {
    char *original;
    char *key;
} StringEntry;

int compare_entries(const void *a, const void *b) {
    const StringEntry *e1 = (const StringEntry *)a;
    const StringEntry *e2 = (const StringEntry *)b;
    return strcmp(e1->key, e2->key);
}

void sort_strings_posix(char **array, size_t count, const char *locale_name) {
    locale_t loc = newlocale(LC_ALL_MASK, locale_name, NULL);
    if (!loc) {
        perror("newlocale failed");
        return;
    }

    StringEntry *entries = malloc(count * sizeof(StringEntry));
    if (!entries) {
        freelocale(loc);
        return;
    }

    for (size_t i = 0; i < count; ++i) {
        entries[i].original = array[i];
        
        // Визначення необхідного розміру ключа
        size_t len = strxfrm_l(NULL, array[i], 0, loc) + 1;
        entries[i].key = malloc(len);
        if (entries[i].key) {
            strxfrm_l(entries[i].key, array[i], len, loc);
        }
    }

    qsort(entries, count, sizeof(StringEntry), compare_entries);

    for (size_t i = 0; i < count; ++i) {
        array[i] = entries[i].original;
        free(entries[i].key);
    }

    free(entries);
    freelocale(loc);
}
