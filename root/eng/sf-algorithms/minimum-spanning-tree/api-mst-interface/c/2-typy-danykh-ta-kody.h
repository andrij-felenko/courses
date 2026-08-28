#ifndef MST_TYPES_H
#define MST_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок та статусів виконання операцій */
typedef enum {
    MST_STATUS_SUCCESS            = 0,  /* Успішний розрахунок повного кістякового дерева */
    MST_STATUS_DISCONNECTED_GRAPH = 1,  /* Граф незв'язний: побудовано мінімальний кістяковий ліс */
    MST_STATUS_INVALID_ARGUMENT   = 2,  /* Передано нульовий покажчик або некоректні розміри */
    MST_STATUS_VERTEX_OUT_OF_BOUNDS = 3,/* Індекс вершини виходить за межі діапазону [0, V-1] */
    MST_STATUS_OUT_OF_MEMORY      = 4   /* Помилка виділення динамічної пам'яті */
} MstStatusCode;

/* Алгоритмічний бекенд для виконання розрахунку */
typedef enum {
    MST_ALGO_AUTO    = 0, /* Автоматичний вибір стратегії за щільністю графа */
    MST_ALGO_PRIM    = 1, /* Алгоритм Прима–Ярніка на базі індексованої двійкової купи */
    MST_ALGO_BORUVKA = 2  /* Алгоритм Борувки на базі лісу неперетинних множин */
} MstAlgorithmType;

/* Дескриптор зваженого ребра */
typedef struct {
    int32_t u;        /* Перша вершина ребра */
    int32_t v;        /* Друга вершина ребра */
    int64_t weight;   /* Вага ребра (допустимі будь-які дійсні цілі значення) */
} MstEdgeDesc;

/* Структура збереження результатів розрахунку */
typedef struct {
    MstEdgeDesc *edges;       /* Суцільний масив ребер, що увійшли до кістяка */
    size_t edge_count;        /* Загальна кількість ребер у знайденому розв'язку */
    int64_t total_weight;     /* Точна сумарна вага кістякового дерева або лісу */
    size_t num_components;    /* Кількість компонент зв'язності (1 для дерева, >1 для лісу) */
    MstStatusCode status;     /* Фінальний статус виконання розрахунку */
} MstSolution;

#ifdef __cplusplus
}
#endif

#endif /* MST_TYPES_H */
