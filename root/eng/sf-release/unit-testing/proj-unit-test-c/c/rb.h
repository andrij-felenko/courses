/* rb.h — обіцянка назовні, і більше нічого */
#ifndef RB_H
#define RB_H

#include <stdbool.h>
#include <stddef.h>

#ifndef RB_CAP
#  define RB_CAP 256u          /* у прошивці 256; тестова збірка ставить своє */
#endif
_Static_assert((RB_CAP & (RB_CAP - 1u)) == 0u, "RB_CAP має бути степенем двійки");

typedef struct {
    int    data[RB_CAP];
    size_t head;               /* куди писати наступний  */
    size_t tail;               /* звідки читати наступний */
    size_t count;              /* скільки лежить зараз    */
} rb_t;

void   rb_init (rb_t *r);
bool   rb_push (rb_t *r, int x);        /* false — повний, вміст не змінено */
bool   rb_pop  (rb_t *r, int *out);     /* false — порожній, *out не чіпано */
size_t rb_count(const rb_t *r);

#endif
