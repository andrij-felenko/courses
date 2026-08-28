#include <stdio.h>
#include <stdlib.h>

#define TERM       0x7fffffff   /* «рівень» термінала — нижче за будь-яку змінну */
#define BDD_FALSE  0            /* вузол-константа 0 */
#define BDD_TRUE   1            /* вузол-константа 1 */

typedef struct {
    int var;        /* індекс змінної: 0 — найвища за порядком; термінал → TERM */
    int lo, hi;     /* нащадки: гілки «0» і «1» (теж індекси) */
    int next;       /* наступний вузол у ланцюжку кошика унікальної таблиці, -1 — кінець */
    int ref;        /* лічильник посилань */
} Node;

static Node *nodes;             /* пул вузлів; вузол — це індекс сюди */
static int   ncap, nnodes;

static int  *utable;            /* унікальна таблиця: кошик → голова ланцюжка (індекс) */
static int   umask;             /* розмір−1 (розмір — степінь двійки) */

typedef struct { int f, g, h, r; } Cache;
static Cache *ctable;           /* кеш операцій: слот → трійка ITE та її результат */
static int    cmask;

static unsigned hash3(int a, int b, int c) {
    unsigned x = (unsigned)a * 73856093u ^ (unsigned)b * 19349663u ^ (unsigned)c * 83492791u;
    return x ^ (x >> 13);
}

static void bdd_init(int cap, int ubits, int cbits) {
    ncap = cap; nodes = malloc(sizeof(Node) * ncap);
    umask = (1 << ubits) - 1; utable = malloc(sizeof(int) * (umask + 1));
    for (int i = 0; i <= umask; i++) utable[i] = -1;
    cmask = (1 << cbits) - 1; ctable = malloc(sizeof(Cache) * (cmask + 1));
    for (int i = 0; i <= cmask; i++) ctable[i].f = -1;      /* −1 = порожній слот */
    nodes[0] = (Node){ TERM, 0, 0, -1, 1 };                 /* константа 0 */
    nodes[1] = (Node){ TERM, 1, 1, -1, 1 };                 /* константа 1 */
    nnodes = 2;
}
