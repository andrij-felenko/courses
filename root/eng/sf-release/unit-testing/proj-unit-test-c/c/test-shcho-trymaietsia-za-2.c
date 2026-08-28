typedef struct {
    int      data[RB_CAP];
    uint32_t written;                      /* скільки всього покладено */
    uint32_t read;                         /* скільки всього забрано  */
    uint32_t dropped;
} rb_t;

#define RB_IDX(pos) ((size_t)((pos) & (RB_CAP - 1u)))

void rb_init(rb_t *r) { r->written = 0; r->read = 0; r->dropped = 0; }

bool rb_push(rb_t *r, int x) {
    if (r->written - r->read >= RB_CAP) { r->dropped++; return false; }
    r->data[RB_IDX(r->written)] = x;
    r->written++;
    return true;
}

bool rb_pop(rb_t *r, int *out) {
    if (r->written == r->read) return false;
    *out = r->data[RB_IDX(r->read)];
    r->read++;
    return true;
}

size_t rb_count(const rb_t *r) { return (size_t)(r->written - r->read); }
