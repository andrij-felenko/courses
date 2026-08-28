#ifndef KRUSKAL_API_H
#define KRUSKAL_API_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Статуси виконання алгоритму
typedef enum {
    KRUSKAL_OK = 0,
    KRUSKAL_DISCONNECTED_FOREST = 1,
    KRUSKAL_ERR_INVALID_VERTEX = -1,
    KRUSKAL_ERR_NULL_POINTER = -2,
    KRUSKAL_ERR_NO_MEMORY = -3
} KruskalStatus;

// Компактна структура представлення ребра
typedef struct {
    uint32_t u;
    uint32_t v;
    int64_t weight;
} KruskalEdge;

// Опис графа для передачі в модуль
typedef struct {
    uint32_t num_vertices;
    size_t num_edges;
    KruskalEdge *edges;
} KruskalGraph;

// Результат побудови мінімального кістяка
typedef struct {
    KruskalEdge *mst_edges;      // Динамічно виділений масив відібраних ребер
    size_t edge_count;           // Кількість ребер у дереві або лісі
    int64_t total_weight;        // Сумарна вага кістяка
    uint32_t num_components;     // Кількість отриманих компонент зв'язності
} KruskalResult;

/**
 * @brief Обчислює мінімальне кістякове дерево або ліс графа методом Краскала.
 * 
 * @param[in]  graph   Вказівник на ініціалізовану структуру графа. Масив edges буде відсортовано.
 * @param[out] result  Вказівник на структуру, куди записуються результати обчислення.
 * 
 * @return KruskalStatus Код результату операції.
 */
KruskalStatus kruskal_compute_mst(KruskalGraph *graph, KruskalResult *result);

/**
 * @brief Звільняє динамічні ресурси, виділені під час обчислення результату.
 * 
 * @param[in,out] result Вказівник на структуру результату для очищення.
 */
void kruskal_free_result(KruskalResult *result);

#ifdef __cplusplus
}
#endif

#endif // KRUSKAL_API_H
