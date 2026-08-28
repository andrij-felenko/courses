#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint32_t max_rtt_ms;
    uint32_t failed_edges_count;
} NetworkTimeoutContextC;

static void c_on_examine_edge_timeout(int u, int v, void* user_data) {
    NetworkTimeoutContextC* ctx = (NetworkTimeoutContextC*)user_data;
    // Імітація перевірки RTT
    uint32_t simulated_rtt = (u * 17 + v * 31) % 150;
    if (simulated_rtt > ctx->max_rtt_ms) {
        ctx->failed_edges_count++;
    }
}

void run_network_bfs_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start,
    uint32_t timeout_threshold
) {
    NetworkTimeoutContextC ctx = {timeout_threshold, 0};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.examine_edge = c_on_examine_edge_timeout;

    c_bfs_run(num_vertices, adj_lists, adj_sizes, start, &visitor);
    printf("Кількість ребер із тайм-аутом: %u\n", ctx.failed_edges_count);
}
