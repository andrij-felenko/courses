#ifndef MATCHING_SOLVER_H
#define MATCHING_SOLVER_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди помилок та станів виконання розв'язувача паросполучень.
 */
typedef enum {
    MATCHING_SUCCESS = 0,             /**< Операція виконана успішно */
    MATCHING_ERR_NULL_POINTER = -1,   /**< Передано нульовий вказівник у якості аргумента */
    MATCHING_ERR_INVALID_VERTEX = -2, /**< Індекс вершини виходить за дозволені межі [0, V-1] */
    MATCHING_ERR_OUT_OF_MEMORY = -3,  /**< Не вдалося виділити пам'ять у системній купі */
    MATCHING_ERR_NOT_BIPARTITE = -4,  /**< Вхідний граф не є двочастковим (для алгоритму Хофкрофта-Карпа) */
    MATCHING_ERR_ALGORITHM_FAIL = -5 /**< Внутрішній обчислювальний збій розв'язувача */
} matching_error_t;

/**
 * @brief Перелік алгоритмів розв'язання задачі паросполучення.
 */
typedef enum {
    MATCHING_ALG_EDMONDS_BLOSSOM = 0, /**< Детермінований алгоритм Едмондса для загальних графів (O(V²E)) */
    MATCHING_ALG_HOPCROFT_KARP = 1,   /**< Алгоритм Хофкрофта-Карпа для двочасткових графів (O(E√V)) */
    MATCHING_ALG_LOVASZ_RANDOM = 2    /**< Рандомізований алгебраїчний тест матриці Тутте (O(nʷ)) */
} matching_algorithm_t;

/**
 * @brief Структура, що описує окреме ребро у паросполученні.
 */
typedef struct {
    int32_t u; /**< Початкова вершина ребра */
    int32_t v; /**< Кінцева вершина ребра */
} matching_edge_t;

/**
 * @brief Результат обчислення паросполучення.
 */
typedef struct {
    int32_t matching_size;      /**< Загальна кількість ребер у максимальному паросполученні */
    bool is_perfect;            /**< Чи є паросполучення досконалим (покриває всі V вершин) */
    matching_edge_t* edges;     /**< Динамічний масив ребер паросполучення */
    size_t num_edges;           /**< Кількість елементів у масиві edges */
} matching_result_t;

/**
 * @brief Непрозорий тип (opaque handle) графа.
 */
typedef struct matching_graph matching_graph_t;

/**
 * @brief Створити екземпляр графа з заданою кількістю вершин.
 * @param num_vertices Кількість вершин у графі (повинна бути > 0)
 * @param out_graph Вихідний вказівник на створений об'єкт графа
 * @return MATCHING_SUCCESS у разі успіху або відповідний код помилки
 */
matching_error_t matching_graph_create(int32_t num_vertices, matching_graph_t** out_graph);

/**
 * @brief Знищити граф та звільнити всі пов'язані з ним ресурси.
 * @param graph Об'єкт графа для знищення (безпечно передавати NULL)
 */
void matching_graph_destroy(matching_graph_t* graph);

/**
 * @brief Додати неороієнтоване ребро між вершинами u та v.
 * @param graph Об'єкт графа
 * @param u Індекс першої вершини (0 <= u < V)
 * @param v Індекс другої вершини (0 <= v < V)
 * @return MATCHING_SUCCESS або код помилки MATCHING_ERR_INVALID_VERTEX
 */
matching_error_t matching_graph_add_edge(matching_graph_t* graph, int32_t u, int32_t v);

/**
 * @brief Обчислити паросполучення обраним алгоритмом.
 * @param graph Об'єкт графа
 * @param algorithm Алгоритм для обчислення
 * @param out_result Вихідна структура для збереження результату
 * @return MATCHING_SUCCESS або код помилки
 */
matching_error_t matching_solve(const matching_graph_t* graph,
                                 matching_algorithm_t algorithm,
                                 matching_result_t* out_result);

/**
 * @brief Звільнити пам'ять масиву ребер у структурі результату.
 * @param result Результат обчислення для очищення
 */
void matching_result_free(matching_result_t* result);

#ifdef __cplusplus
}
#endif

#endif /* MATCHING_SOLVER_H */
