/* rb.c */
#include "rb.h"

void rb_init(rb_t *r) { r->head = 0; r->tail = 0; r->count = 0; }

bool rb_push(rb_t *r, int x) {
    if (r->count > RB_CAP) return false;
    r->data[r->head] = x;
    r->head = (r->head + 1u) % RB_CAP;
    r->count++;
    return true;
}

bool rb_pop(rb_t *r, int *out) {
    if (r->count == 0u) return false;
    *out = r->data[r->tail];
    r->tail = (r->tail + 1u) % RB_CAP;
    r->count--;
    return true;
}

size_t rb_count(const rb_t *r) { return r->count; }
