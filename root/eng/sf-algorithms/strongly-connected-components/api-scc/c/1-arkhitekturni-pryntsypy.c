#include <stddef.h>
#include <stdbool.h>

/* Повертаний результат обчислення компонент сильної зв'язаності */
typedef struct {
    int num_vertices;       /* Загальна кількість вершин у вихідному графі */
    int num_scc;            /* Кількість виявлених компонент сильної зв'язаності */
    int* comp_id;           /* Масив розміру num_vertices: comp_id[u] — ID компоненти u (0..num_scc-1) */
    int* scc_sizes;         /* Масив розміру num_scc: кількість вершин у кожній компоненті */
    int** scc_members;      /* Двовимірний масив: scc_members[i][j] — j-та вершина i-тої SCC */
} SCCResult;

/* Структура графа конденсації (DAG) */
typedef struct {
    int num_scc;            /* Кількість мета-вершин (дорівнює SCCResult.num_scc) */
    int num_dag_edges;      /* Загальна кількість унікальних мета-ребер у DAG */
    int** dag_adj;          /* Список суміжності DAG: dag_adj[i] містить сусіди компоненти i */
    int* dag_degrees;       /* Вихідні ступені мета-вершин у DAG */
    int* in_degrees;        /* Вхідні ступені мета-вершин у DAG */
} CondensationGraph;

/* Конфігураційні параметри обчислювального модуля */
typedef struct {
    bool enable_condensation; /* Автоматично будувати граф конденсації */
    bool check_invariants;   /* Виконувати перевірку діапазону індексів вершин */
    size_t stack_capacity;   /* Початковий розмір внутрішнього стека */
} SCCConfig;
