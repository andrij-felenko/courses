/* stack_safe.c — реалізація №3: потокобезпечна, з м'ютексом.
 * Заголовок ТОЙ САМИЙ. Клієнт той самий. */
#include "stack.h"
#include <stdlib.h>
#include <threads.h>

#define STACK_CAP 64

struct Stack {
    int    data[STACK_CAP];
    size_t top;
    mtx_t  lock;            /* м'ютекс — теж усередині, клієнт його не бачить */
};

Stack *stack_new(void) {
    Stack *s = malloc(sizeof *s);
    if (s == NULL) return NULL;
    if (mtx_init(&s->lock, mtx_plain) != thrd_success) {
        free(s);
        return NULL;
    }
    s->top = 0;
    return s;
}

bool stack_push(Stack *s, int v) {
    mtx_lock(&s->lock);              /* заходимо — двері на замок */
    bool ok = false;
    if (s->top < STACK_CAP) {
        s->data[s->top++] = v;
        ok = true;
    }
    mtx_unlock(&s->lock);            /* виходимо — двері відмикаємо */
    return ok;
}

bool stack_pop(Stack *s, int *out) {
    mtx_lock(&s->lock);
    bool ok = false;
    if (s->top > 0) {
        *out = s->data[--s->top];
        ok = true;
    }
    mtx_unlock(&s->lock);
    return ok;
}

size_t stack_size(const Stack *s) {
    /* const заважає замкнути lock (mtx_lock хоче не-const).
     * Читання одного size_t на більшості платформ атомарне саме собою,
     * тож для розміру блокування можна опустити — але це рішення
     * реалізації, і воно теж НЕ протікає в заголовок. */
    return s->top;
}

void stack_free(Stack *s) {
    if (s == NULL) return;
    mtx_destroy(&s->lock);   /* знищити м'ютекс ПЕРЕД звільненням пам'яті */
    free(s);
}
