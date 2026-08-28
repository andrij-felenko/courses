/* mv_register.h / mv_register.c */
#include "vector_clock.h"

#define MAX_VERSIONS 8
#define MAX_VAL_LEN 64

typedef struct {
    char value[MAX_VAL_LEN];
    vector_clock_t clock;
} mvr_entry_t;

typedef struct {
    mvr_entry_t entries[MAX_VERSIONS];
    size_t count;
} mv_register_t;

void mvr_init(mv_register_t *reg) {
    reg->count = 0;
}

void mvr_write(mv_register_t *reg, const char *val, const char *actor, vector_clock_t ctx) {
    vc_increment(&ctx, actor);
    mvr_entry_t next[MAX_VERSIONS];
    size_t n_count = 0;

    /* Додаємо новий запис */
    strncpy(next[n_count].value, val, MAX_VAL_LEN - 1);
    next[n_count].value[MAX_VAL_LEN - 1] = '\0';
    next[n_count].clock = ctx;
    n_count++;

    /* Фільтруємо старі версії */
    for (size_t i = 0; i < reg->count; ++i) {
        vc_relation_t rel = vc_compare(&reg->entries[i].clock, &ctx);
        if (rel == VC_CONCURRENT || rel == VC_AFTER) {
            if (n_count < MAX_VERSIONS) {
                next[n_count++] = reg->entries[i];
            }
        }
    }

    memcpy(reg->entries, next, sizeof(mvr_entry_t) * n_count);
    reg->count = n_count;
}

void mvr_merge(mv_register_t *dst, const mv_register_t *src) {
    mvr_entry_t next[MAX_VERSIONS];
    size_t n_count = 0;

    for (size_t i = 0; i < dst->count; ++i) {
        bool dominated = false;
        for (size_t j = 0; j < src->count; ++j) {
            if (vc_compare(&dst->entries[i].clock, &src->entries[j].clock) == VC_BEFORE) {
                dominated = true;
                break;
            }
        }
        if (!dominated && n_count < MAX_VERSIONS) {
            next[n_count++] = dst->entries[i];
        }
    }

    for (size_t j = 0; j < src->count; ++j) {
        bool dominated = false;
        for (size_t i = 0; i < dst->count; ++i) {
            vc_relation_t rel = vc_compare(&src->entries[j].clock, &dst->entries[i].clock);
            if (rel == VC_BEFORE || rel == VC_EQUAL) {
                dominated = true;
                break;
            }
        }
        if (!dominated && n_count < MAX_VERSIONS) {
            next[n_count++] = src->entries[j];
        }
    }

    memcpy(dst->entries, next, sizeof(mvr_entry_t) * n_count);
    dst->count = n_count;
}
