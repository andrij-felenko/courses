#include <stdint.h>
#include <stdbool.h>

#define HLD_MAX_NODES 200005
#define HLD_SUCCESS    0
#define HLD_ERR_BOUNDS -1
#define HLD_ERR_CYCLE  -2
#define HLD_ERR_DISCON -3

typedef struct {
    int to;
    int next;
} hld_edge_t;

typedef struct {
    int n;                          /* Кількість вершин у дереві (0 .. n-1) */
    int root;                       /* Індекс кореневої вершини */
    int edge_cnt;                   /* Поточна кількість доданих спрямованих ребер */
    int cur_pos;                    /* Лічильник поточної позиції лінеаризації DFS */

    int head_edge[HLD_MAX_NODES];   /* Голова списку суміжності для кожної вершини */
    hld_edge_t edges[HLD_MAX_NODES * 2]; /* Масив спрямованих ребер */

    int parent[HLD_MAX_NODES];      /* Батьківський вузол у кореневому дереві */
    int depth[HLD_MAX_NODES];       /* Глибина вершини від кореня (корінь = 0) */
    int sz[HLD_MAX_NODES];          /* Розмір піддерева вершини */
    int heavy[HLD_MAX_NODES];       /* Індекс важкого сина (-1 якщо лист) */
    int head[HLD_MAX_NODES];        /* Голова важкого ланцюга */
    int pos[HLD_MAX_NODES];         /* Позиція вершини у лінеаризованому масиві */
    int inv_pos[HLD_MAX_NODES];     /* Зворотна таблиця: індекс вершини за позицією */

    int64_t node_val[HLD_MAX_NODES];/* Початкові значення у вершинах */
    int64_t flat_val[HLD_MAX_NODES];/* Значення, впорядковані за DFS-індексами */

    int64_t seg_tree[HLD_MAX_NODES * 4]; /* Значення агрегатів дерева відрізків */
    int64_t seg_lazy[HLD_MAX_NODES * 4]; /* Відкладені операції (Lazy Propagation) */
} hld_tree_t;
