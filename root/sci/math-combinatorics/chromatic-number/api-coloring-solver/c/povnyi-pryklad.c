#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "coloring_solver.h"

int main(void) {
    ColoringGraph* graph = NULL;
    ColoringErrorCode err = coloring_graph_create(11, &graph);
    if (err != COLORING_OK) {
        fprintf(stderr, "Помилка виділення пам'яті для графа: %d\n", err);
        return EXIT_FAILURE;
    }

    /* Побудова ребер графа Грьотча M4 */
    /* Базовий цикл C5: 0-1-2-3-4-0 */
    coloring_graph_add_edge(graph, 0, 1);
    coloring_graph_add_edge(graph, 1, 2);
    coloring_graph_add_edge(graph, 2, 3);
    coloring_graph_add_edge(graph, 3, 4);
    coloring_graph_add_edge(graph, 4, 0);

    /* Тіньові вершини 5..9 з'єднані з сусідами 0..4 */
    coloring_graph_add_edge(graph, 5, 1);
    coloring_graph_add_edge(graph, 5, 4);
    coloring_graph_add_edge(graph, 6, 0);
    coloring_graph_add_edge(graph, 6, 2);
    coloring_graph_add_edge(graph, 7, 1);
    coloring_graph_add_edge(graph, 7, 3);
    coloring_graph_add_edge(graph, 8, 2);
    coloring_graph_add_edge(graph, 8, 4);
    coloring_graph_add_edge(graph, 9, 0);
    coloring_graph_add_edge(graph, 9, 3);

    /* Верхівка 10 з'єднана з усіма тінями 5..9 */
    for (int i = 5; i <= 9; ++i) {
        coloring_graph_add_edge(graph, 10, i);
    }

    /* Налаштування конфігурації Branch-and-Price */
    ColoringConfig config;
    coloring_config_default(&config);
    config.engine = COLORING_ENGINE_BRANCH_AND_PRICE;
    config.time_limit_ms = 10000;
    config.symmetry_breaking_level = 2;

    ColoringResult result;
    memset(&result, 0, sizeof(result));
    ColoringDiagnostics diag;
    memset(&diag, 0, sizeof(diag));

    printf("Запуск розв'язувача Branch-and-Price...\n");
    err = coloring_solve(graph, &config, &result, &diag);
    if (err != COLORING_OK) {
        fprintf(stderr, "Помилка розв'язання: %s (код %d)\n", diag.error_message, err);
        coloring_graph_free(graph);
        return EXIT_FAILURE;
    }

    printf("Статус: %d, Хроматичне число: %d (час: %llu мкс)\n",
           result.status, result.chromatic_number, (unsigned long long)result.elapsed_us);
    printf("Розподіл кольорів по вершинах:\n");
    for (int v = 0; v < graph->num_vertices; ++v) {
        printf("  Вершина %2d -> Колір %d\n", v, result.colors[v]);
    }

    /* Верифікація сертифіката */
    err = coloring_verify_result(graph, &result, &diag);
    if (err == COLORING_OK) {
        printf("Сертифікат розфарбування успішно верифіковано: колізій немає.\n");
    } else {
        fprintf(stderr, "Помилка верифікації! Конфлікт на ребрі (%d, %d)\n",
                diag.conflict_u, diag.conflict_v);
    }

    /* Експорт у JSON */
    coloring_export_json("grotzsch_result.json", graph, &result);

    /* Звільнення ресурсів */
    coloring_result_free(&result);
    coloring_graph_free(graph);

    return EXIT_SUCCESS;
}
