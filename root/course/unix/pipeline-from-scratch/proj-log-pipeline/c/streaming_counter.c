/* streaming_counter.c — швидкісний потоковий агрегатор логів на мові C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <signal.h>
#include <unistd.h>

#define HASH_CAPACITY 65536
#define MAX_IP_LEN 46

typedef struct Entry {
    char ip[MAX_IP_LEN];
    uint64_t count;
    struct Entry *next;
} Entry;

typedef struct {
    Entry *buckets[HASH_CAPACITY];
    uint64_t total_errors;
} HashTable;

/* Алгоритм швидкого хешування рядків djb2 (Dan Bernstein) */
static uint32_t hash_string(const char *str) {
    uint32_t hash = 5381;
    int c;
    while ((c = (unsigned char)*str++)) {
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
    }
    return hash % HASH_CAPACITY;
}

static void ht_add(HashTable *ht, const char *ip) {
    uint32_t idx = hash_string(ip);
    Entry *cur = ht->buckets[idx];
    while (cur) {
        if (strcmp(cur->ip, ip) == 0) {
            cur->count++;
            ht->total_errors++;
            return;
        }
        cur = cur->next;
    }
    Entry *new_node = malloc(sizeof(Entry));
    if (!new_node) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    strncpy(new_node->ip, ip, MAX_IP_LEN - 1);
    new_node->ip[MAX_IP_LEN - 1] = '\0';
    new_node->count = 1;
    new_node->next = ht->buckets[idx];
    ht->buckets[idx] = new_node;
    ht->total_errors++;
}

static void ht_free(HashTable *ht) {
    for (size_t i = 0; i < HASH_CAPACITY; i++) {
        Entry *cur = ht->buckets[i];
        while (cur) {
            Entry *tmp = cur;
            cur = cur->next;
            free(tmp);
        }
    }
}

int main(void) {
    /* Ігноруємо SIGPIPE, щоб уникнути аварійного завершення при закритті пайпу споживачем */
    signal(SIGPIPE, SIG_IGN);

    HashTable ht = {0};
    char *line = NULL;
    size_t len = 0;
    ssize_t read_bytes;

    /* Швидке потокове читання з stdin за допомогою системного буфера getline() */
    while ((read_bytes = getline(&line, &len, stdin)) != -1) {
        if (read_bytes < 10) continue;

        /* Пошук IP-адреси (перше поле до першого пробілу) без виділення пам'яті */
        char *ip_end = strchr(line, ' ');
        if (!ip_end) continue;
        *ip_end = '\0';
        const char *ip = line;

        /* Пошук HTTP-статусу після лапок запиту: " 502 " */
        char *quote = strchr(ip_end + 1, '"');
        if (!quote) continue;
        char *second_quote = strchr(quote + 1, '"');
        if (!second_quote) continue;

        char *status_ptr = second_quote + 1;
        while (*status_ptr == ' ') status_ptr++;

        /* Перевірка чи код статусу починається з 5xx */
        if (status_ptr[0] == '5' && status_ptr[1] >= '0' && status_ptr[1] <= '9' &&
            status_ptr[2] >= '0' && status_ptr[2] <= '9') {
            ht_add(&ht, ip);
        }
    }

    free(line);

    /* Друк результатів у стандартний вивід */
    for (size_t i = 0; i < HASH_CAPACITY; i++) {
        Entry *cur = ht.buckets[i];
        while (cur) {
            printf("%lu %s\n", cur->count, cur->ip);
            cur = cur->next;
        }
    }

    ht_free(&ht);
    return EXIT_SUCCESS;
}
