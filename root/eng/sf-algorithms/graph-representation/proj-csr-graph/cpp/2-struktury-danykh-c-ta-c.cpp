#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <memory>
#include <algorithm>

/* Динамічний граф для зручного додавання ребер під час завантаження */
class DynamicGraph {
public:
    explicit DynamicGraph(uint32_t num_vertices)
        : adj_(num_vertices) {}

    void add_edge(uint32_t u, uint32_t v) {
        if (u < adj_.size()) {
            adj_[u].push_back(v);
        }
    }

    [[nodiscard]] uint32_t num_vertices() const noexcept {
        return static_cast<uint32_t>(adj_.size());
    }

    [[nodiscard]] std::span<const uint32_t> neighbors(uint32_t u) const noexcept {
        if (u >= adj_.size()) return {};
        return adj_[u];
    }

    [[nodiscard]] const std::vector<std::vector<uint32_t>>& raw_adjacency() const noexcept {
        return adj_;
    }

private:
    std::vector<std::vector<uint32_t>> adj_;
};

/* Статичний CSR граф: максимальна кеш-локальність та нульовий оверхед вказівників */
class CsrGraph {
public:
    explicit CsrGraph(const DynamicGraph& dg)
        : offsets_(dg.num_vertices() + 1, 0) {
        
        size_t total_edges = 0;
        for (uint32_t i = 0; i < dg.num_vertices(); ++i) {
            total_edges += dg.neighbors(i).size();
        }
        edges_.resize(total_edges);

        uint32_t current_offset = 0;
        for (uint32_t i = 0; i < dg.num_vertices(); ++i) {
            offsets_[i] = current_offset;
            for (uint32_t neighbor : dg.neighbors(i)) {
                edges_[current_offset++] = neighbor;
            }
        }
        offsets_[dg.num_vertices()] = current_offset;
    }

    [[nodiscard]] uint32_t num_vertices() const noexcept {
        return static_cast<uint32_t>(offsets_.size() - 1);
    }

    [[nodiscard]] size_t num_edges() const noexcept {
        return edges_.size();
    }

    /* Швидкий доступ до зрізу сусідів без виділення пам'яті */
    [[nodiscard]] std::span<const uint32_t> neighbors(uint32_t u) const noexcept {
        if (u + 1 >= offsets_.size()) return {};
        uint32_t start = offsets_[u];
        uint32_t end = offsets_[u + 1];
        return {edges_.data() + start, end - start};
    }

    [[nodiscard]] uint32_t degree(uint32_t u) const noexcept {
        if (u + 1 >= offsets_.size()) return 0;
        return offsets_[u + 1] - offsets_[u];
    }

private:
    std::vector<uint32_t> offsets_;
    std::vector<uint32_t> edges_;
};
