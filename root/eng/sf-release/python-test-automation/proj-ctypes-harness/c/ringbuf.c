/* ringbuf.c — кільцевий буфер байтів. Повний буфер витісняє найстаріший. */
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>

#ifdef _WIN32
#  define RB_API __declspec(dllexport)
#else
#  define RB_API __attribute__((visibility("default")))
#endif

struct rb {
    uint8_t *data;       /* сховище на cap байтів                  */
    size_t   cap;        /* місткість, завжди > 0                  */
    size_t   head;       /* куди покласти наступний байт           */
    size_t   tail;       /* звідки взяти найстаріший               */
    size_t   len;        /* скільки байтів усередині зараз         */
    uint8_t  owns_data;  /* чи звільняти сховище в rb_destroy      */
    uint8_t  overrun;    /* чи витісняли хоч раз найстаріший байт  */
};

RB_API struct rb *rb_create(size_t cap)
{
    if (cap == 0) return NULL;
    struct rb *b = calloc(1, sizeof *b);
    if (!b) return NULL;
    b->data = malloc(cap);
    if (!b->data) { free(b); return NULL; }
    b->cap = cap;
    b->owns_data = 1;
    return b;
}

/* Варіант для прошивки: сховище дає викликач, malloc не потрібен. */
RB_API void rb_init(struct rb *b, uint8_t *storage, size_t cap)
{
    memset(b, 0, sizeof *b);
    b->data = storage;
    b->cap  = cap;
}

RB_API struct rb *rb_create_static(uint8_t *storage, size_t cap)
{
    if (!storage || cap == 0) return NULL;
    struct rb *b = calloc(1, sizeof *b);
    if (!b) return NULL;
    rb_init(b, storage, cap);
    return b;
}

RB_API void rb_destroy(struct rb *b)
{
    if (!b) return;
    if (b->owns_data) free(b->data);
    free(b);
}

/* Повертає 1, якщо найстаріший байт довелося витіснити, інакше 0. */
RB_API int rb_push(struct rb *b, uint8_t v)
{
    int displaced = 0;
    b->data[b->head] = v;
    b->head = (b->head + 1) % b->cap;
    if (b->len < b->cap) {
        b->len++;
    } else {
        b->overrun = 1;
        displaced = 1;
    }
    return displaced;
}

/* Повертає 0 і кладе байт за адресою out; -1, якщо буфер порожній. */
RB_API int rb_pop(struct rb *b, uint8_t *out)
{
    if (b->len == 0) return -1;
    *out = b->data[b->tail];
    b->tail = (b->tail + 1) % b->cap;
    b->len--;
    return 0;
}

RB_API size_t rb_len(const struct rb *b) { return b->len; }

/* Самоопис розкладки — щоб обв'язка могла звірити своє уявлення з дійсністю. */
RB_API size_t rb_sizeof(void) { return sizeof(struct rb); }

RB_API size_t rb_offset(const char *field)
{
    if (!strcmp(field, "data"))      return offsetof(struct rb, data);
    if (!strcmp(field, "cap"))       return offsetof(struct rb, cap);
    if (!strcmp(field, "head"))      return offsetof(struct rb, head);
    if (!strcmp(field, "tail"))      return offsetof(struct rb, tail);
    if (!strcmp(field, "len"))       return offsetof(struct rb, len);
    if (!strcmp(field, "owns_data")) return offsetof(struct rb, owns_data);
    if (!strcmp(field, "overrun"))   return offsetof(struct rb, overrun);
    return (size_t)-1;
}
