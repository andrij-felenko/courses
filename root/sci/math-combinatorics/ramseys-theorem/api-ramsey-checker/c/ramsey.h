/* ramsey.h - ANSI C99/C11 API Interface */
#ifndef LIBRAMSEY_H
#define LIBRAMSEY_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання */
typedef enum {
    RAMSEY_SUCCESS             =  0,
    RAMSEY_ERROR_INVALID_PARAM = -1,
    RAMSEY_ERROR_NO_MEMORY     = -2,
    RAMSEY_ERROR_OVERFLOW      = -3,
    RAMSEY_ERROR_TIMEOUT       = -4,
    RAMSEY_ERROR_IO            = -5
} ramsey_status_t;

/* Структура представлення двокольорового графа Рамсея */
typedef struct {
    size_t num_vertices;     /* Кількість вершин n (1 <= n <= 64) */
    uint64_t *adj_matrix;    /* Динамічний масив бітових масок (розмір n) */
} ramsey_graph_t;

/* Результат аналізу монохроматичних підграфів */
typedef struct {
    bool has_monochromatic_clique;  /* true, якщо знайдено кліку K_r або K_s */
    size_t found_clique_size;       /* Розмір знайденої кліки */
    bool is_red_clique;             /* true для червоного кольору, false для синього */
    uint64_t clique_mask;           /* Бітова маска вершин, що утворюють кліку */
} ramsey_clique_result_t;

/* Створення та знищення графа */
ramsey_status_t ramsey_graph_create(ramsey_graph_t **graph, size_t n);
void ramsey_graph_destroy(ramsey_graph_t *graph);

/* Маніпуляції з ребрами */
ramsey_status_t ramsey_graph_set_edge(ramsey_graph_t *graph, size_t u, size_t v, bool is_red);
ramsey_status_t ramsey_graph_get_edge(const ramsey_graph_t *graph, size_t u, size_t v, bool *out_is_red);

/* Перевірка та пошук клік */
ramsey_status_t ramsey_graph_check_clique(const ramsey_graph_t *graph, size_t r, size_t s, ramsey_clique_result_t *result);
ramsey_status_t ramsey_find_counterexample(ramsey_graph_t *out_graph, size_t n, size_t r, size_t s, uint32_t timeout_sec);

/* Серіалізація та експорт */
ramsey_status_t ramsey_graph_export_json(const ramsey_graph_t *graph, const char *filepath);
ramsey_status_t ramsey_graph_import_json(ramsey_graph_t **out_graph, const char *filepath);
ramsey_status_t ramsey_graph_export_dimacs(const ramsey_graph_t *graph, const char *filepath);

#ifdef __cplusplus
}
#endif

#endif /* LIBRAMSEY_H */
