#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* Метрика відстані */
typedef enum {
    NN_METRIC_L2 = 0,             /* Квадрат або лінійна евклідова відстань */
    NN_METRIC_COSINE = 1,         /* Косинусна кутова відстань: 1 - cos(theta) */
    NN_METRIC_INNER_PRODUCT = 2   /* Скалярний добуток: -<u, v> (для максимального добутку) */
} nn_metric_type_t;

/* Тип алгоритмічного рушія індексу */
typedef enum {
    NN_ENGINE_FLAT_SCAN = 0,      /* Точний паралельний SIMD-скан */
    NN_ENGINE_METRIC_TREE = 1,    /* Метричне дерево (VP-Tree / Ball-Tree) */
    NN_ENGINE_GRAPH_HNSW = 2,     /* Наближений ієрархічний граф (HNSW) */
    NN_ENGINE_QUANTIZED_IVF = 3   /* Інвертований індекс із квантуванням (IVF-PQ) */
} nn_engine_type_t;

/* Коди результатів виконання операцій */
typedef enum {
    NN_SUCCESS = 0,
    NN_ERR_INVALID_ARGUMENT = -1,
    NN_ERR_OUT_OF_MEMORY = -2,
    NN_ERR_DIMENSION_MISMATCH = -3,
    NN_ERR_INDEX_NOT_BUILT = -4,
    NN_ERR_CONCURRENCY_VIOLATION = -5
} nn_status_t;

/* Конфігурація для створення індексу */
typedef struct {
    int dimension;                /* Розмірність векторного простору D */
    nn_metric_type_t metric;      /* Метрика відстані */
    nn_engine_type_t engine;      /* Архітектурний тип індексу */
    size_t initial_capacity;      /* Очікувана початкова кількість точок N */
    float approximation_factor;   /* Епсилон (epsilon) для наближеного пошуку (0 = точно) */
    int num_threads;              /* Кількість потоків для побудови та пакетного пошуку */
} nn_config_t;

/* Діагностичні метрики виконання окремого запиту */
typedef struct {
    size_t distance_evaluations;  /* Реальна кількість виконаних обчислень відстаней */
    size_t nodes_visited;         /* Кількість відвіданих вузлів дерева чи вершин графа */
    double latency_microseconds;  /* Тривалість виконання запиту в мікросекундах */
    float recall_estimate;        /* Оцінка Recall відносно точного скану */
} nn_search_stats_t;

/* Контейнер результатів пошуку */
typedef struct {
    int64_t *ids;                 /* Масив ідентифікаторів знайдених точок розміром k */
    float *distances;             /* Масив відстаней до знайдених точок розміром k */
    size_t count;                 /* Фактична кількість повернених точок (<= k) */
    size_t capacity;              /* Виділений розмір буферів */
} nn_result_set_t;

/* Непрозорий покажчик на екземпляр індексу */
typedef struct nn_index nn_index_t;
