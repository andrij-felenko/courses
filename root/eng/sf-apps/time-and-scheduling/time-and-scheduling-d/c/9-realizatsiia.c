#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define WHEEL_L0_BITS  8
#define WHEEL_L0_SIZE  (1U << WHEEL_L0_BITS)
#define WHEEL_L0_MASK  (WHEEL_L0_SIZE - 1)

#define WHEEL_LVL_BITS 6
#define WHEEL_LVL_SIZE (1U << WHEEL_LVL_BITS)
#define WHEEL_LVL_MASK (WHEEL_LVL_SIZE - 1)

typedef struct timer_entry timer_entry_t;
typedef void (*timer_fn)(timer_entry_t *entry, void *arg);

struct timer_entry {
    uint64_t expires_tick;
    timer_fn callback;
    void *arg;
    timer_entry_t *next;
    timer_entry_t *prev;
    int wheel;
    int slot;
    bool active;
};

typedef struct {
    timer_entry_t *head;
} wheel_bucket_t;

typedef struct {
    uint64_t current_tick;
    wheel_bucket_t l0[WHEEL_L0_SIZE];
    wheel_bucket_t l1[WHEEL_LVL_SIZE];
    wheel_bucket_t l2[WHEEL_LVL_SIZE];
    wheel_bucket_t l3[WHEEL_LVL_SIZE];
    uint64_t l0_mask[WHEEL_L0_SIZE / 64];
    uint64_t l1_mask;
    uint64_t l2_mask;
    uint64_t l3_mask;
} htw_scheduler_t;

void htw_init(htw_scheduler_t *s) {
    memset(s, 0, sizeof(*s));
}

static void list_push(wheel_bucket_t *b, timer_entry_t *e) {
    e->next = b->head;
    e->prev = NULL;
    if (b->head) b->head->prev = e;
    b->head = e;
}

static void list_del(wheel_bucket_t *b, timer_entry_t *e) {
    if (e->prev) e->prev->next = e->next;
    else b->head = e->next;
    if (e->next) e->next->prev = e->prev;
    e->next = e->prev = NULL;
}

void htw_add(htw_scheduler_t *s, timer_entry_t *e, uint64_t expires, timer_fn cb, void *arg) {
    e->expires_tick = expires;
    e->callback = cb;
    e->arg = arg;
    e->active = true;

    if (expires <= s->current_tick) {
        int slot = (int)(s->current_tick & WHEEL_L0_MASK);
        list_push(&s->l0[slot], e);
        s->l0_mask[slot / 64] |= (1ULL << (slot % 64));
        e->wheel = 0;
        e->slot = slot;
        return;
    }

    uint64_t delta = expires - s->current_tick;
    if (delta < (1ULL << 8)) {
        int slot = (int)(expires & WHEEL_L0_MASK);
        list_push(&s->l0[slot], e);
        s->l0_mask[slot / 64] |= (1ULL << (slot % 64));
        e->wheel = 0; e->slot = slot;
    } else if (delta < (1ULL << 14)) {
        int slot = (int)((expires >> 8) & WHEEL_LVL_MASK);
        list_push(&s->l1[slot], e);
        s->l1_mask |= (1ULL << slot);
        e->wheel = 1; e->slot = slot;
    } else if (delta < (1ULL << 20)) {
        int slot = (int)((expires >> 14) & WHEEL_LVL_MASK);
        list_push(&s->l2[slot], e);
        s->l2_mask |= (1ULL << slot);
        e->wheel = 2; e->slot = slot;
    } else {
        int slot = (int)((expires >> 20) & WHEEL_LVL_MASK);
        list_push(&s->l3[slot], e);
        s->l3_mask |= (1ULL << slot);
        e->wheel = 3; e->slot = slot;
    }
}

void htw_cancel(htw_scheduler_t *s, timer_entry_t *e) {
    if (!e->active) return;
    if (e->wheel == 0) {
        list_del(&s->l0[e->slot], e);
        if (!s->l0[e->slot].head) s->l0_mask[e->slot / 64] &= ~(1ULL << (e->slot % 64));
    } else if (e->wheel == 1) {
        list_del(&s->l1[e->slot], e);
        if (!s->l1[e->slot].head) s->l1_mask &= ~(1ULL << e->slot);
    } else if (e->wheel == 2) {
        list_del(&s->l2[e->slot], e);
        if (!s->l2[e->slot].head) s->l2_mask &= ~(1ULL << e->slot);
    } else if (e->wheel == 3) {
        list_del(&s->l3[e->slot], e);
        if (!s->l3[e->slot].head) s->l3_mask &= ~(1ULL << e->slot);
    }
    e->active = false;
}
