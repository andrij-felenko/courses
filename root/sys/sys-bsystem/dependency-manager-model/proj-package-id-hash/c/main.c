#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAX_ENTRIES 32
#define MAX_STR_LEN 128

typedef struct {
    char key[MAX_STR_LEN];
    char val[MAX_STR_LEN];
} KeyValue;

typedef struct {
    KeyValue entries[MAX_ENTRIES];
    size_t count;
} ConfigMap;

static void map_add(ConfigMap *m, const char *k, const char *v) {
    if (m->count >= MAX_ENTRIES) return;
    strncpy(m->entries[m->count].key, k, MAX_STR_LEN - 1);
    m->entries[m->count].key[MAX_STR_LEN - 1] = '\0';
    strncpy(m->entries[m->count].val, v, MAX_STR_LEN - 1);
    m->entries[m->count].val[MAX_STR_LEN - 1] = '\0';
    m->count++;
}

static int compare_entries(const void *a, const void *b) {
    const KeyValue *ka = (const KeyValue *)a;
    const KeyValue *kb = (const KeyValue *)b;
    return strcmp(ka->key, kb->key);
}

/* 64-бітний алгоритм FNV-1a для детермінованого обчислення дайджесту */
static uint64_t compute_hash_fnv1a(const char *data, size_t len) {
    uint64_t hash = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint8_t)data[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

void compute_package_id(ConfigMap *settings, ConfigMap *options, ConfigMap *deps, char out_id[32]) {
    /* Сортуємо всі словники за алфавітом ключів */
    qsort(settings->entries, settings->count, sizeof(KeyValue), compare_entries);
    qsort(options->entries, options->count, sizeof(KeyValue), compare_entries);
    if (deps) {
        qsort(deps->entries, deps->count, sizeof(KeyValue), compare_entries);
    }

    char canonical[4096] = {0};
    size_t offset = 0;

    for (size_t i = 0; i < settings->count; ++i) {
        int n = snprintf(canonical + offset, sizeof(canonical) - offset,
                         "s:%s=%s\n", settings->entries[i].key, settings->entries[i].val);
        if (n > 0) offset += (size_t)n;
    }
    for (size_t i = 0; i < options->count; ++i) {
        int n = snprintf(canonical + offset, sizeof(canonical) - offset,
                         "o:%s=%s\n", options->entries[i].key, options->entries[i].val);
        if (n > 0) offset += (size_t)n;
    }
    if (deps) {
        for (size_t i = 0; i < deps->count; ++i) {
            int n = snprintf(canonical + offset, sizeof(canonical) - offset,
                             "r:%s=%s\n", deps->entries[i].key, deps->entries[i].val);
            if (n > 0) offset += (size_t)n;
        }
    }

    uint64_t h = compute_hash_fnv1a(canonical, offset);
    snprintf(out_id, 32, "pkg_%016llx", (unsigned long long)h);
}

int main(void) {
    ConfigMap settings = { .count = 0 };
    map_add(&settings, "os", "Linux");
    map_add(&settings, "arch", "x86_64");
    map_add(&settings, "compiler", "gcc");
    map_add(&settings, "compiler.version", "13");
    map_add(&settings, "compiler.cppstd", "20");
    map_add(&settings, "build_type", "Release");

    ConfigMap options = { .count = 0 };
    map_add(&options, "shared", "False");
    map_add(&options, "fPIC", "True");

    ConfigMap deps = { .count = 0 };
    map_add(&deps, "zlib", "pkg_e72a084c911b33fa");

    char pkg_id[32];
    compute_package_id(&settings, &options, &deps, pkg_id);

    printf("Розрахований Package ID: %s\n", pkg_id);
    return 0;
}
