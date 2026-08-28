/* stack_array.c — реалізація №1: масив фіксованого розміру.
 * ТІЛЬКИ тут відома справжня будова Stack. */
#include "stack.h"
#include <stdlib.h>

#define STACK_CAP 64        /* стеля: більше 64 чисел не влізе */

/* ОСЬ повне визначення — те, чого клієнт не бачить. */
struct Stack {
    int    data[STACK_CAP]; /* самі числа, у місці */
    size_t top;             /* скільки зайнято (індекс наступного вільного) */
};

Stack *stack_new(void) {
    Stack *s = malloc(sizeof *s);   /* sizeof працює: тут будова ВІДОМА */
    if (s == NULL) return NULL;
    s->top = 0;
    return s;
}

bool stack_push(Stack *s, int v) {
    if (s->top >= STACK_CAP) return false;   /* повний — чесна відмова */
    s->data[s->top] = v;
    s->top++;
    return true;
}

bool stack_pop(Stack *s, int *out) {
    if (s->top == 0) return false;           /* порожній */
    s->top--;
    *out = s->data[s->top];
    return true;
}

size_t stack_size(const Stack *s) {
    return s->top;
}

void stack_free(Stack *s) {
    free(s);                 /* один шматок пам'яті — одне звільнення */
}
