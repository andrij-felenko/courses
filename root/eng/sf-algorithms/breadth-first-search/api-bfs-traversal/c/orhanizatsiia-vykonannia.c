#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint32_t* visited_bits;
    int* queue_buf;
    size_t max_vertices;
} BFSStaticBuffersC;

static inline bool get_bit(const uint32_t* bits, int idx) {
    return (bits[idx / 32] & (1U << (idx % 32))) != 0;
}

static inline void set_bit(uint32_t* bits, int idx) {
    bits[idx / 32] |= (1U << (idx % 32));
}

int c_bfs_run_no_alloc(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start_node,
    BFSStaticBuffersC* buffers,
    const BFSVisitorC* visitor
) {
    if (num_vertices > (int)buffers->max_vertices) {
        return -1; // Переповнення статичного буфера!
    }

    uint32_t* visited = buffers->visited_bits;
    int* queue = buffers->queue_buf;
    int head = 0, tail = 0;

    for (size_t i = 0; i < (size_t)(num_vertices + 31) / 32; ++i) {
        visited[i] = 0;
    }

    set_bit(visited, start_node);
    if (visitor->discover_vertex) {
        visitor->discover_vertex(start_node, visitor->user_data);
    }
    queue[tail++] = start_node;

    while (head < tail) {
        int u = queue[head++];
        if (visitor->examine_vertex) {
            visitor->examine_vertex(u, visitor->user_data);
        }

        for (int i = 0; i < adj_sizes[u]; ++i) {
            int v = adj_lists[u][i];
            if (!get_bit(visited, v)) {
                set_bit(visited, v);
                if (visitor->tree_edge) {
                    visitor->tree_edge(u, v, visitor->user_data);
                }
                queue[tail++] = v;
            }
        }
    }
    return 0; // Успішно без жодного виклику malloc!
}
