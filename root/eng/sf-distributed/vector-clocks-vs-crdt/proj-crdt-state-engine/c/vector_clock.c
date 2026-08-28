/* vector_clock.h / vector_clock.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NODES 16
#define ID_LEN 32

typedef struct {
    char node_id[ID_LEN];
    uint64_t counter;
} vc_entry_t;

typedef struct {
    vc_entry_t entries[MAX_NODES];
    size_t count;
} vector_clock_t;

typedef enum {
    VC_EQUAL,       /* V1 == V2 */
    VC_BEFORE,      /* V1 < V2  (V1 causal ancestor of V2) */
    VC_AFTER,       /* V1 > V2  (V1 causal descendant of V2) */
    VC_CONCURRENT   /* V1 || V2 (conflict / concurrent branch) */
} vc_relation_t;

void vc_init(vector_clock_t *vc) {
    vc->count = 0;
}

uint64_t vc_get(const vector_clock_t *vc, const char *node_id) {
    for (size_t i = 0; i < vc->count; ++i) {
        if (strncmp(vc->entries[i].node_id, node_id, ID_LEN) == 0) {
            return vc->entries[i].counter;
        }
    }
    return 0;
}

void vc_set(vector_clock_t *vc, const char *node_id, uint64_t val) {
    for (size_t i = 0; i < vc->count; ++i) {
        if (strncmp(vc->entries[i].node_id, node_id, ID_LEN) == 0) {
            vc->entries[i].counter = val;
            return;
        }
    }
    if (vc->count < MAX_NODES) {
        strncpy(vc->entries[vc->count].node_id, node_id, ID_LEN - 1);
        vc->entries[vc->count].node_id[ID_LEN - 1] = '\0';
        vc->entries[vc->count].counter = val;
        vc->count++;
    }
}

void vc_increment(vector_clock_t *vc, const char *node_id) {
    uint64_t cur = vc_get(vc, node_id);
    vc_set(vc, node_id, cur + 1);
}

void vc_merge(vector_clock_t *dst, const vector_clock_t *src) {
    for (size_t i = 0; i < src->count; ++i) {
        uint64_t cur = vc_get(dst, src->entries[i].node_id);
        if (src->entries[i].counter > cur) {
            vc_set(dst, src->entries[i].node_id, src->entries[i].counter);
        }
    }
}

vc_relation_t vc_compare(const vector_clock_t *a, const vector_clock_t *b) {
    bool a_has_greater = false;
    bool b_has_greater = false;

    /* Перевіряємо всі ключі з a */
    for (size_t i = 0; i < a->count; ++i) {
        uint64_t ca = a->entries[i].counter;
        uint64_t cb = vc_get(b, a->entries[i].node_id);
        if (ca > cb) a_has_greater = true;
        if (cb > ca) b_has_greater = true;
    }

    /* Перевіряємо ключі з b, яких могло не бути в a */
    for (size_t i = 0; i < b->count; ++i) {
        uint64_t cb = b->entries[i].counter;
        uint64_t ca = vc_get(a, b->entries[i].node_id);
        if (cb > ca) b_has_greater = true;
        if (ca > cb) a_has_greater = true;
    }

    if (!a_has_greater && !b_has_greater) return VC_EQUAL;
    if (a_has_greater && !b_has_greater)  return VC_AFTER;
    if (!a_has_greater && b_has_greater)  return VC_BEFORE;
    return VC_CONCURRENT;
}
