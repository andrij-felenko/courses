#ifndef COLORING_SOLVER_H
#define COLORING_SOLVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define COLORING_MAX_VERTICES_DENSE 1024
#define COLORING_UNCOLORED (-1)

typedef enum {
    COLORING_OK = 0,
    COLORING_ERR_INVALID_ARGUMENT = -1,
    COLORING_ERR_VERTEX_OUT_OF_BOUNDS = -2,
    COLORING_ERR_SELF_LOOP_DETECTED = -3,
    COLORING_ERR_PINNED_CONFLICT = -4,
    COLORING_ERR_OUT_OF_MEMORY = -5,
    COLORING_ERR_TIMEOUT = -6,
    COLORING_ERR_TARGET_INFEASIBLE = -7,
    COLORING_ERR_INVALID_CERTIFICATE = -8,
    COLORING_ERR_IO_FAILURE = -9,
    COLORING_ERR_SOLVER_DIVERGED = -10
} ColoringErrorCode;

typedef enum {
    COLORING_STATUS_UNSOLVED = 0,
    COLORING_STATUS_OPTIMAL = 1,
    COLORING_STATUS_FEASIBLE = 2,
    COLORING_STATUS_INFEASIBLE = 3,
    COLORING_STATUS_TIMEOUT = 4
} ColoringStatus;

typedef enum {
    COLORING_ENGINE_GREEDY_DSATUR = 0,
    COLORING_ENGINE_EXACT_DSATUR = 1,
    COLORING_ENGINE_ILP = 2,
    COLORING_ENGINE_BRANCH_AND_PRICE = 3
} ColoringEngine;

typedef enum {
    COLORING_CERT_NONE = 0,
    COLORING_CERT_MAX_CLIQUE = 1,
    COLORING_CERT_EXHAUSTIVE_TREE = 2,
    COLORING_CERT_DUAL_BOUND_EXHAUSTION = 3
} ColoringCertType;

/* Щільна структура графа на бітових масках */
typedef struct {
    int32_t num_vertices;
    int32_t num_edges;
    uint64_t* adj_matrix;        /* Розмір: num_vertices * ((num_vertices + 63) / 64) */
    int32_t* pinned_colors;      /* Розмір: num_vertices, за замовчуванням COLORING_UNCOLORED */
    double* vertex_weights;      /* Ваги вершин для зваженого розфарбування */
} ColoringGraph;

/* Конфігурація параметрів розв'язувача */
typedef struct {
    ColoringEngine engine;
    uint32_t time_limit_ms;
    int32_t lower_bound_hint;
    int32_t upper_bound_target;
    int32_t symmetry_breaking_level;
    bool enable_kempe_pass;
    uint32_t random_seed;
    size_t memory_limit_bytes;
} ColoringConfig;

/* Сертифікат розфарбування та метрики */
typedef struct {
    ColoringCertType cert_type;
    int32_t cert_size;
    int32_t* cert_vertices;      /* Наприклад, індекси вершин знайденої кліки K_k */
    uint64_t explored_nodes;
    uint64_t generated_columns;
    uint64_t simplex_iterations;
} ColoringCertificate;

/* Структура підсумкового результату */
typedef struct {
    ColoringStatus status;
    int32_t chromatic_number;
    int32_t* colors;             /* Розмір: num_vertices, значення 0 .. chromatic_number - 1 */
    int32_t lower_bound;
    int32_t upper_bound;
    uint64_t elapsed_us;
    ColoringCertificate certificate;
} ColoringResult;

/* Діагностичний звіт */
typedef struct {
    ColoringErrorCode last_error;
    char error_message[256];
    int32_t conflict_u;
    int32_t conflict_v;
    size_t peak_memory_bytes;
} ColoringDiagnostics;

/* Керування життєвим циклом графа */
ColoringErrorCode coloring_graph_create(int32_t num_vertices, ColoringGraph** out_graph);
void coloring_graph_free(ColoringGraph* graph);
ColoringErrorCode coloring_graph_add_edge(ColoringGraph* graph, int32_t u, int32_t v);
ColoringErrorCode coloring_graph_pin_color(ColoringGraph* graph, int32_t v, int32_t color);

/* Ініціалізація стандартної конфігурації */
void coloring_config_default(ColoringConfig* config);

/* Основний виклик розв'язувача */
ColoringErrorCode coloring_solve(
    const ColoringGraph* graph,
    const ColoringConfig* config,
    ColoringResult* result,
    ColoringDiagnostics* diag
);

/* Верифікація коректності та сертифіката */
ColoringErrorCode coloring_verify_result(
    const ColoringGraph* graph,
    const ColoringResult* result,
    ColoringDiagnostics* diag
);

/* Звільнення ресурсів результату */
void coloring_result_free(ColoringResult* result);

/* Серіалізація та десеріалізація */
ColoringErrorCode coloring_import_dimacs(const char* filepath, ColoringGraph** out_graph);
ColoringErrorCode coloring_export_dimacs(const char* filepath, const ColoringGraph* graph);
ColoringErrorCode coloring_export_json(const char* filepath, const ColoringGraph* graph, const ColoringResult* result);

#ifdef __cplusplus
}
#endif

#endif /* COLORING_SOLVER_H */
