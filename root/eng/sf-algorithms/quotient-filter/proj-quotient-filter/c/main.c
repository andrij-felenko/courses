#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_LOAD_FACTOR 0.85

typedef struct {
    uint8_t is_occupied : 1;
    uint8_t is_continuation : 1;
    uint8_t is_shifted : 1;
    uint8_t remainder : 5;  /* 5-бітний залишок для демонстрації в 1 байті */
} QFSlot;

typedef struct {
    QFSlot *table;
    size_t q_bits;          /* Кількість бітів частки */
    size_t r_bits;          /* Кількість бітів залишку */
    size_t num_slots;       /* m = 1 << q_bits */
    size_t slot_mask;       /* num_slots - 1 */
    size_t count;           /* Кількість збережених елементів */
} QuotientFilter;

/* 64-бітний хешер FNV-1a */
static inline uint64_t hash_bytes(const void *data, size_t len) {
    const uint8_t *ptr = (const uint8_t *)data;
    uint64_t h = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        h ^= ptr[i];
        h *= 1099511628211ULL;
    }
    return h;
}

/* Ініціалізація квошієнтного фільтра */
QuotientFilter *qf_create(size_t q_bits, size_t r_bits) {
    QuotientFilter *qf = (QuotientFilter *)malloc(sizeof(QuotientFilter));
    if (!qf) return NULL;

    qf->q_bits = q_bits;
    qf->r_bits = r_bits;
    qf->num_slots = (size_t)1 << q_bits;
    qf->slot_mask = qf->num_slots - 1;
    qf->count = 0;
    qf->table = (QFSlot *)calloc(qf->num_slots, sizeof(QFSlot));

    if (!qf->table) {
        free(qf);
        return NULL;
    }
    return qf;
}

void qf_destroy(QuotientFilter *qf) {
    if (qf) {
        free(qf->table);
        free(qf);
    }
}

static inline bool slot_is_empty(const QFSlot *s) {
    return !s->is_occupied && !s->is_continuation && !s->is_shifted;
}

/* Знаходження початку набігу для канонічного слота f_q */
static size_t find_run_start(const QuotientFilter *qf, size_t f_q) {
    size_t curr = f_q;
    while (qf->table[curr].is_shifted) {
        curr = (curr - 1) & qf->slot_mask;
    }

    size_t scan = curr;
    size_t run_start = curr;

    while (scan != f_q) {
        do {
            run_start = (run_start + 1) & qf->slot_mask;
        } while (qf->table[run_start].is_continuation);

        do {
            scan = (scan + 1) & qf->slot_mask;
        } while (!qf->table[scan].is_occupied);
    }
    return run_start;
}

/* Перевірка наявності ключа у фільтрі */
bool qf_lookup(const QuotientFilter *qf, const void *key, size_t len) {
    uint64_t hash = hash_bytes(key, len);
    size_t f_q = (hash >> qf->r_bits) & qf->slot_mask;
    uint8_t f_r = (uint8_t)(hash & (((uint64_t)1 << qf->r_bits) - 1));

    if (!qf->table[f_q].is_occupied) {
        return false;
    }

    size_t curr = find_run_start(qf, f_q);

    do {
        if (qf->table[curr].remainder == f_r) {
            return true;
        }
        if (qf->table[curr].remainder > f_r) {
            return false;
        }
        curr = (curr + 1) & qf->slot_mask;
    } while (qf->table[curr].is_continuation);

    return false;
}

/* Вставка нового елемента в квошієнтний фільтр */
bool qf_insert(QuotientFilter *qf, const void *key, size_t len) {
    if ((double)qf->count / (double)qf->num_slots >= MAX_LOAD_FACTOR) {
        return false;
    }

    uint64_t hash = hash_bytes(key, len);
    size_t f_q = (hash >> qf->r_bits) & qf->slot_mask;
    uint8_t f_r = (uint8_t)(hash & (((uint64_t)1 << qf->r_bits) - 1));

    if (slot_is_empty(&qf->table[f_q])) {
        qf->table[f_q].is_occupied = 1;
        qf->table[f_q].is_continuation = 0;
        qf->table[f_q].is_shifted = 0;
        qf->table[f_q].remainder = f_r;
        qf->count++;
        return true;
    }

    if (!qf->table[f_q].is_occupied) {
        /* Канонічний слот порожній від своїх, але зайнятий чужим зсунутим елементом */
        qf->table[f_q].is_occupied = 1;
    }

    size_t insert_pos = find_run_start(qf, f_q);
    bool has_run = qf->table[f_q].is_occupied;

    if (has_run) {
        while (qf->table[insert_pos].remainder < f_r && qf->table[(insert_pos + 1) & qf->slot_mask].is_continuation) {
            insert_pos = (insert_pos + 1) & qf->slot_mask;
        }
        if (qf->table[insert_pos].remainder < f_r) {
            insert_pos = (insert_pos + 1) & qf->slot_mask;
        }
    }

    /* Каскадний зсув вправо для звільнення insert_pos */
    QFSlot prev_slot = { .is_occupied = 0, .is_continuation = 0, .is_shifted = (insert_pos != f_q), .remainder = f_r };
    size_t curr = insert_pos;

    while (true) {
        QFSlot temp = qf->table[curr];
        bool was_empty = slot_is_empty(&temp);

        qf->table[curr].remainder = prev_slot.remainder;
        qf->table[curr].is_shifted = (curr != f_q);
        if (curr == insert_pos && has_run && insert_pos != find_run_start(qf, f_q)) {
            qf->table[curr].is_continuation = 1;
        }

        if (was_empty) break;

        prev_slot = temp;
        prev_slot.is_shifted = 1;
        curr = (curr + 1) & qf->slot_mask;
    }

    qf->count++;
    return true;
}

/* Детерміноване видалення елемента */
bool qf_delete(QuotientFilter *qf, const void *key, size_t len) {
    uint64_t hash = hash_bytes(key, len);
    size_t f_q = (hash >> qf->r_bits) & qf->slot_mask;
    uint8_t f_r = (uint8_t)(hash & (((uint64_t)1 << qf->r_bits) - 1));

    if (!qf->table[f_q].is_occupied) return false;

    size_t run_start = find_run_start(qf, f_q);
    size_t target = run_start;
    bool found = false;

    do {
        if (qf->table[target].remainder == f_r) {
            found = true;
            break;
        }
        target = (target + 1) & qf->slot_mask;
    } while (qf->table[target].is_continuation);

    if (!found) return false;

    /* Зсув кластера вліво для заповнення дірки */
    size_t curr = target;
    while (true) {
        size_t next = (curr + 1) & qf->slot_mask;
        if (slot_is_empty(&qf->table[next]) || !qf->table[next].is_shifted) {
            memset(&qf->table[curr], 0, sizeof(QFSlot));
            break;
        }
        qf->table[curr].remainder = qf->table[next].remainder;
        qf->table[curr].is_continuation = qf->table[next].is_continuation;
        qf->table[curr].is_shifted = (curr != f_q);
        curr = next;
    }

    qf->count--;
    return true;
}
