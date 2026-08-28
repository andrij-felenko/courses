#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Модель внутрішньопроцесної агрегації на C (аналог поведінки AWK)
typedef struct HashEntry {
    char key[64];
    long count;
    struct HashEntry *next;
} HashEntry;

#define HASH_BUCKETS 65536
static HashEntry* buckets[HASH_BUCKETS];

static unsigned int hash_key(const char *s) {
    unsigned int h = 5381;
    while (*s) h = ((h << 5) + h) + (unsigned char)(*s++);
    return h % HASH_BUCKETS;
}

void process_stream_in_process(FILE *stream) {
    char *line = NULL;
    size_t cap = 0;
    ssize_t len;

    while ((len = getline(&line, &cap, stream)) != -1) {
        if (strstr(line, "ERROR") == NULL) continue; // Етап grep

        // Етап cut: виділення 4-го стовпця за пробілом
        char *saveptr;
        char *token = strtok_r(line, " \t\n", &saveptr);
        for (int i = 1; i < 4 && token; ++i) {
            token = strtok_r(NULL, " \t\n", &saveptr);
        }
        if (!token) continue;

        // Етап uniq -c: оновлення лічильника в хеш-таблиці
        unsigned int idx = hash_key(token);
        HashEntry *entry = buckets[idx];
        while (entry && strcmp(entry->key, token) != 0) entry = entry->next;

        if (entry) {
            entry->count++;
        } else {
            HashEntry *new_entry = (HashEntry*)malloc(sizeof(HashEntry));
            strncpy(new_entry->key, token, sizeof(new_entry->key) - 1);
            new_entry->key[sizeof(new_entry->key) - 1] = '\0';
            new_entry->count = 1;
            new_entry->next = buckets[idx];
            buckets[idx] = new_entry;
        }
    }
    free(line);

    // Вивід результатів
    for (int i = 0; i < HASH_BUCKETS; ++i) {
        for (HashEntry *e = buckets[i]; e; e = e->next) {
            printf("%7ld %s\n", e->count, e->key);
        }
    }
}
