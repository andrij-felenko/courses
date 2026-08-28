/* C11 implementation: Savitch's deterministic reachability algorithm */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_VERTICES 64

typedef struct {
    uint32_t num_vertices;
    bool adj[MAX_VERTICES][MAX_VERTICES];
} Graph;

/* 
 * Savitch's recursive reachability check.
 * Evaluates if vertex 'v' is reachable from 'u' in at most 'steps' edges.
 * Stack depth is limited to O(log2 N), each frame uses O(log2 N) memory.
 */
bool savitch_can_reach(const Graph *g, uint32_t u, uint32_t v, uint32_t steps) {
    if (u == v) {
        return true;
    }
    if (steps == 1) {
        return g->adj[u][v];
    }

    uint32_t half_steps = (steps + 1) / 2;

    /* Iterate over all potential intermediate vertices w */
    for (uint32_t w = 0; w < g->num_vertices; ++w) {
        if (savitch_can_reach(g, u, w, half_steps)) {
            if (savitch_can_reach(g, w, v, steps - half_steps)) {
                return true;
            }
        }
    }

    return false;
}

int main(void) {
    Graph g = { .num_vertices = 5 };
    
    /* Construct graph edges */
    g.adj[0][1] = true;
    g.adj[1][2] = true;
    g.adj[2][3] = true;
    g.adj[3][4] = true;

    uint32_t start_vertex = 0;
    uint32_t target_vertex = 4;

    bool reachable = savitch_can_reach(&g, start_vertex, target_vertex, g.num_vertices);

    if (reachable) {
        printf("Vertex %u is REACHABLE from %u\n", target_vertex, start_vertex);
    } else {
        printf("Vertex %u is NOT reachable from %u\n", target_vertex, start_vertex);
    }

    return 0;
}
