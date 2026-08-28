/* main.c — клієнт. Вмикає ЛИШЕ заголовок, будови не бачить. */
#include "stack.h"
#include <stdio.h>

int main(void) {
    Stack *s = stack_new();
    if (s == NULL) { fprintf(stderr, "нема пам'яті\n"); return 1; }

    for (int i = 1; i <= 5; i++)
        stack_push(s, i * 10);        /* 10, 20, 30, 40, 50 */

    printf("розмір: %zu\n", stack_size(s));   /* 5 */

    int v;
    while (stack_pop(s, &v))          /* знімаємо, поки є що */
        printf("зняв %d\n", v);       /* 50, 40, 30, 20, 10 — LIFO */

    stack_free(s);
    return 0;
}
