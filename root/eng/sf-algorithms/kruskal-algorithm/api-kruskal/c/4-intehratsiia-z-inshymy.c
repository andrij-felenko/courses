#include "kruskal_api.h"
#include <stdio.h>

void run_example(void) {
    KruskalEdge edges[] = {
        {0, 1, 10}, {0, 2, 6}, {0, 3, 5},
        {1, 3, 15}, {2, 3, 4}
    };
    KruskalGraph graph = { 4, 5, edges };
    KruskalResult result;

    if (kruskal_compute_mst(&graph, &result) == KRUSKAL_OK) {
        printf("Кістяк знайдено, вага: %lld\n", (long long)result.total_weight);
        kruskal_free_result(&result);
    }
}
