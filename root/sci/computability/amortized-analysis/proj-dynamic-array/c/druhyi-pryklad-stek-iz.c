#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int   *data;
    size_t len, cap;
    unsigned long long moves;   // реальні переміщення: кожен запис і кожен зняток
} Stack;

void st_push(Stack *s, int x) {
    if (s->len == s->cap) {
        size_t nc = s->cap ? s->cap * 2 : 1;
        s->data = realloc(s->data, nc * sizeof(int));
        s->cap  = nc;
    }
    s->data[s->len++] = x;
    s->moves++;                                  // один запис
}

size_t st_multipop(Stack *s, size_t k) {
    size_t popped = 0;
    while (k-- && s->len) {                       // знімаємо min(k, len)
        s->len--;
        s->moves++;                               // один зняток
        popped++;
    }
    return popped;
}

int main(void) {
    Stack s = {0};
    unsigned ops = 0, pushes = 0;

    for (int i = 0; i < 20; i++) { st_push(&s, i); ops++; pushes++; }
    st_multipop(&s, 100); ops++;                  // ДОРОГИЙ виклик: зняв усі 20
    for (int i = 0; i < 5; i++)  { st_push(&s, i); ops++; pushes++; }
    st_multipop(&s, 3);   ops++;                  // зняв 3
    st_push(&s, 99);      ops++; pushes++;
    st_multipop(&s, 100); ops++;                  // зняв рештку 3

    printf("операцій: %u,  штовхань: %u,  переміщень: %llu\n", ops, pushes, s.moves);
    printf("межа 2·штовхань = %u  ≥  переміщень %llu\n", 2 * pushes, s.moves);
    free(s.data);
    return 0;
}
