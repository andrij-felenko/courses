#include "sedbuf.h"

#include <stdlib.h>
#include <string.h>

void sed_fatal(const char *what) {
    fprintf(stderr, "mini-sed: %s\n", what);
    exit(4);
}

void sedbuf_init(SedBuffer *b) {
    b->data = NULL;
    b->len = 0;
    b->cap = 0;
}

void sedbuf_free(SedBuffer *b) {
    free(b->data);
    sedbuf_init(b);
}

void sedbuf_reserve(SedBuffer *b, size_t need) {
    /* need — корисні байти; місце під '\0' докладаємо самі, тому строга нерівність */
    if (b->cap > need) return;

    size_t cap = b->cap + b->cap / 2;          /* коефіцієнт росту 1.5x */
    if (cap <= need) cap = need + 1;
    cap = (cap + 63u) & ~(size_t)63u;          /* вирівнювання за блоком 64 байти */
    if (cap <= need) sed_fatal("переповнення розміру буфера");

    char *p = realloc(b->data, cap);
    if (!p) sed_fatal("не вдалося перерозподілити буфер");
    b->data = p;
    b->cap = cap;
    b->data[b->len] = '\0';                    /* інваріант тримається й після росту */
}

void sedbuf_assign(SedBuffer *b, const char *src, size_t len) {
    sedbuf_reserve(b, len);
    if (len) memcpy(b->data, src, len);
    b->len = len;
    b->data[len] = '\0';
}

void sedbuf_append(SedBuffer *b, const char *src, size_t len) {
    sedbuf_reserve(b, b->len + len);
    if (len) memcpy(b->data + b->len, src, len);
    b->len += len;
    b->data[b->len] = '\0';
}

void sedbuf_append_byte(SedBuffer *b, char c) {
    sedbuf_append(b, &c, 1);
}

void sedbuf_clear(SedBuffer *b) {
    b->len = 0;
    if (b->data) b->data[0] = '\0';
}

void sed_state_init(SedState *st) {
    memset(st, 0, sizeof *st);   /* заразом гасить усі прапорці стану */
}

void sed_state_free(SedState *st) {
    sedbuf_free(&st->pattern_space);
    sedbuf_free(&st->hold_space);
}

void sed_hold(SedState *st) {
    sedbuf_assign(&st->hold_space, st->pattern_space.data, st->pattern_space.len);
}

void sed_hold_append(SedState *st) {
    /* На старті Hold Space порожній, тож перше H дає провідний '\n' —
       саме тому в скриптах пишуть ідіому 1h; 1!H. */
    sedbuf_append_byte(&st->hold_space, '\n');
    sedbuf_append(&st->hold_space, st->pattern_space.data, st->pattern_space.len);
}

void sed_get(SedState *st) {
    sedbuf_assign(&st->pattern_space, st->hold_space.data, st->hold_space.len);
}

void sed_get_append(SedState *st) {
    sedbuf_append_byte(&st->pattern_space, '\n');
    sedbuf_append(&st->pattern_space, st->hold_space.data, st->hold_space.len);
}

void sed_exchange(SedState *st) {
    /* Ні виділення пам'яті, ні копіювання байтів: міняються самі дескриптори. */
    SedBuffer tmp = st->pattern_space;
    st->pattern_space = st->hold_space;
    st->hold_space = tmp;
}

void sed_zap(SedState *st) {
    sedbuf_clear(&st->pattern_space);
}

void sed_delete(SedState *st) {
    sedbuf_clear(&st->pattern_space);
    st->deleted = true;
}

bool sed_delete_first_line(SedState *st) {
    SedBuffer *ps = &st->pattern_space;
    char *nl = ps->len ? memchr(ps->data, '\n', ps->len) : NULL;
    if (!nl) {                       /* немає '\n' — поводимось точно як d */
        sed_delete(st);
        return false;
    }
    size_t head = (size_t)(nl + 1 - ps->data);
    memmove(ps->data, nl + 1, ps->len - head);
    ps->len -= head;
    ps->data[ps->len] = '\0';
    return true;
}

void sed_print(const SedState *st, FILE *out, int sep) {
    if (st->pattern_space.len)
        fwrite(st->pattern_space.data, 1, st->pattern_space.len, out);
    putc(sep, out);
}

void sed_print_first_line(const SedState *st, FILE *out, int sep) {
    const SedBuffer *ps = &st->pattern_space;
    const char *nl = ps->len ? memchr(ps->data, '\n', ps->len) : NULL;
    size_t n = nl ? (size_t)(nl - ps->data) : ps->len;
    if (n) fwrite(ps->data, 1, n, out);
    putc(sep, out);
}

bool sed_read_record(SedState *st, FILE *in, int sep) {
    sedbuf_clear(&st->pattern_space);
    st->deleted = false;

    bool got_any = false;
    int c;
    /* getc іде через буфер stdio, тож це не системний виклик на кожен байт. */
    while ((c = getc(in)) != EOF) {
        got_any = true;
        if (c == sep) break;
        sedbuf_append_byte(&st->pattern_space, (char)c);
    }
    if (!got_any) return false;

    st->line_number++;
    int peek = getc(in);             /* адреса $ вимагає зазирнути на байт уперед */
    if (peek == EOF) st->is_last_line = true;
    else ungetc(peek, in);
    return true;
}
