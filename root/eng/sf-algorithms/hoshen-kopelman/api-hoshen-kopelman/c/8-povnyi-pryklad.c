#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

/* Демонстраційний приклад використання C API */
int run_c_api_demo(void) {
    const int W = 6, H = 6;
    const uint8_t lattice[36] = {
        1, 1, 0, 1, 1, 0,
        1, 0, 0, 0, 1, 0,
        1, 1, 1, 1, 1, 0,
        0, 0, 0, 0, 0, 1,
        0, 1, 1, 0, 0, 1,
        0, 1, 1, 0, 0, 0
    };

    hk_context_t* ctx = NULL;
    hk_error_t err = hk_context_create_2d(&ctx, W, H, HK_CONNECTIVITY_4, HK_BOUNDARY_OPEN);
    if (err != HK_SUCCESS) {
        fprintf(stderr, "Помилка створення контексту: %d\n", err);
        return 1;
    }

    int* labeled_matrix = (int*)malloc((size_t)(W * H) * sizeof(int));
    if (!labeled_matrix) {
        hk_context_destroy(ctx);
        return 1;
    }

    /* Потокове сканування по рядках */
    for (int r = 0; r < H; ++r) {
        hk_process_row(ctx, &lattice[r * W], &labeled_matrix[r * W]);
    }

    /* Фіналізація та ренумерація */
    hk_finalize(ctx);
    hk_relabel_grid(ctx, labeled_matrix, (size_t)(W * H));

    hk_stats_t stats;
    hk_get_stats(ctx, &stats);

    printf("=== Результати аналізу перколації ===\n");
    printf("Кількість кластерів: %d\n", stats.total_clusters);
    printf("Найбільший кластер:   %d вузлів\n", stats.max_cluster_size);
    printf("Середній розмір S(p): %.3f\n", stats.mean_cluster_size);
    printf("Протікання (Y):       %s\n", stats.has_spanning_cluster_y ? "ТАК" : "НІ");

    free(labeled_matrix);
    hk_context_destroy(ctx);
    return 0;
}
