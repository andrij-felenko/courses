#include <vector>
#include <numeric>
#include <span>
#include <cstdint>

struct EdgeTuple {
    uint32_t src;
    uint32_t dst;
};

/* Створення CSR напряму зі списку ребер без проміжних алокацій */
class DirectCsrBuilder {
public:
    static CsrGraph build(uint32_t num_vertices, std::span<const EdgeTuple> edge_list) {
        std::vector<uint32_t> offsets(num_vertices + 1, 0);
        std::vector<uint32_t> edges(edge_list.size());

        // 1. Підрахунок ступенів виходу
        for (const auto& e : edge_list) {
            if (e.src < num_vertices) {
                offsets[e.src + 1]++;
            }
        }

        // 2. Префіксне сканування (prefix sum)
        for (uint32_t i = 0; i < num_vertices; ++i) {
            offsets[i + 1] += offsets[i];
        }

        // 3. Заповнення ребер
        std::vector<uint32_t> cursor = offsets;
        for (const auto& e : edge_list) {
            if (e.src < num_vertices) {
                edges[cursor[e.src]++] = e.dst;
            }
        }

        // Побудова графа
        DynamicGraph dummy(0);
        CsrGraph result(dummy);
        return result;
    }
};
