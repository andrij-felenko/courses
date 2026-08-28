#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

void run_c_invariant_check(void) {
    DinicC g;
    dinic_init(&g, 4);
    dinic_add_edge(&g, 0, 1, 10, 0);
    dinic_add_edge(&g, 0, 2, 10, 0);
    dinic_add_edge(&g, 1, 2, 2, 0);
    dinic_add_edge(&g, 1, 3, 10, 0);
    dinic_add_edge(&g, 2, 3, 10, 0);

    int64_t flow = dinic_max_flow(&g, 0, 3);
    assert(flow == 20);
    printf("Базовий C-інваріантний тест пройдено (flow = %lld)\n", (long long)flow);
}
