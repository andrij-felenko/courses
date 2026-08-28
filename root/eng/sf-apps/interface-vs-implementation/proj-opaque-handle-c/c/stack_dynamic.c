/* stack_dynamic.c — реалізація №2: масив, що росте сам.
 * Заголовок той самий. Будова — інша. */
#include "stack.h"
#include <stdlib.h>
#include <stdint.h>   /* SIZE_MAX — для перевірки переповнення */

struct Stack {
    int    *data;   /* масив у КУПІ, а не в тілі структури */
    size_t  len;    /* скільки зайнято */
    size_t  cap;    /* скільки виділено (місткість) */
};

#define INIT_CAP 8

Stack *stack_new(void) {
    Stack *s = malloc(sizeof *s);
    if (s == NULL) return NULL;
    s->data = malloc(INIT_CAP * sizeof *s->data);
    if (s->data == NULL) { free(s); return NULL; }   /* прибрати за собою */
    s->len = 0;
    s->cap = INIT_CAP;
    return s;
}

/* Виростити місткість удвічі, з перевіркою переповнення size_t. */
static bool grow(Stack *s) {
    size_t new_cap = s->cap * 2;

    /* Перевірка переповнення: якщо подвоєння перескочило через нуль
     * (стало не більшим за старе) — далі рости нікуди. */
    if (new_cap <= s->cap) return false;

    /* Друга перевірка: new_cap * sizeof(int) теж не має переповнити. */
    if (new_cap > SIZE_MAX / sizeof *s->data) return false;

    int *bigger = realloc(s->data, new_cap * sizeof *s->data);
    if (bigger == NULL) return false;   /* realloc не вдався — старе ціле */

    s->data = bigger;
    s->cap  = new_cap;
    return true;
}

bool stack_push(Stack *s, int v) {
    if (s->len == s->cap)            /* місце скінчилось — ростемо */
        if (!grow(s)) return false;  /* не змогли вирости — чесна відмова */
    s->data[s->len] = v;
    s->len++;
    return true;
}

bool stack_pop(Stack *s, int *out) {
    if (s->len == 0) return false;
    s->len--;
    *out = s->data[s->len];
    return true;
}

size_t stack_size(const Stack *s) {
    return s->len;
}

void stack_free(Stack *s) {
    if (s == NULL) return;
    free(s->data);   /* СПЕРШУ внутрішній масив... */
    free(s);         /* ...ПОТІМ саму структуру. Порядок важливий! */
}
