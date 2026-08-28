#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int    *data;               // блок пам'яті під елементи
    size_t  len, cap;           // зайнято / вміщає
    double  factor;             // коефіцієнт росту: 2.0, 1.5 або 1.0 (=«+1»)
    unsigned long long copies;  // скільки елементів скопійовано за весь пробіг
    unsigned           reallocs;// скільки разів росли
    size_t             peak;    // найбільша місткість, яку тримали
} Vec;

// Наступна місткість за коефіцієнтом. Ключова тонкість — гарантований приріст:
// коли cap мале, cap*1.5 може округлитись донизу до cap, і масив завис би навіки.
static size_t grow(size_t cap, double f) {
    if (cap == 0) return 1;                 // перший блок
    size_t nc = (size_t)(cap * f);
    if (nc <= cap) nc = cap + 1;            // приріст хоч на один — інакше глухий кут
    return nc;
}

void push(Vec *v, int x) {
    if (v->len == v->cap) {                     // місця немає — треба рости
        size_t nc = grow(v->cap, v->factor);
        int *bigger = malloc(nc * sizeof(int));
        for (size_t i = 0; i < v->len; i++)     // копіюємо ВСЕ старе: O(len)
            bigger[i] = v->data[i];
        v->copies += v->len;                     // ← ось де лічимо реальну роботу
        v->reallocs++;
        free(v->data);
        v->data = bigger;
        v->cap  = nc;
        if (nc > v->peak) v->peak = nc;
    }
    v->data[v->len++] = x;                        // дешевий запис: O(1)
}

int main(void) {
    const size_t N = 1000000;                     // мільйон додатків
    double      factor[] = {2.0, 1.5, 1.0};
    const char *name[]   = {"× 2", "× 1.5", "+ 1"};

    printf("коеф.   копіювань          росли    пік. місткість   копій/додаток\n");
    for (int f = 0; f < 3; f++) {
        Vec v = {0};                              // усе в нулі: data=NULL, len=cap=0
        v.factor = factor[f];
        for (size_t i = 0; i < N; i++)
            push(&v, (int)i);
        printf("%-6s %14llu %8u %16zu %13.3f\n",
               name[f], v.copies, v.reallocs, v.peak,
               (double)v.copies / N);
        free(v.data);
    }
    return 0;
}
