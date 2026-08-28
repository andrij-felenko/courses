#include <iostream>
#include <vector>
#include <optional>

class Graph {
public:
    explicit Graph(size_t n) : n_(n), adj_(n, std::vector<bool>(n, false)) {}

    void add_edge(size_t u, size_t v) {
        adj_[u][v] = true;
        adj_[v][u] = true;
    }

    [[nodiscard]] size_t size() const { return n_; }
    [[nodiscard]] bool has_edge(size_t u, size_t v) const { return adj_[u][v]; }

private:
    size_t n_;
    std::vector<std::vector<bool>> adj_;
};

class VF2Matcher {
public:
    static std::optional<std::vector<int>> find_isomorphism(const Graph& g1, const Graph& g2) {
        if (g1.size() != g2.size()) return std::nullopt;

        size_t n = g1.size();
        std::vector<int> core1(n, -1);
        std::vector<int> core2(n, -1);

        if (match(g1, g2, core1, core2, 0)) {
            return core1;
        }
        return std::nullopt;
    }

private:
    static bool is_feasible(const Graph& g1, const Graph& g2,
                           const std::vector<int>& core1,
                           const std::vector<int>& core2,
                           size_t u, size_t v) {
        for (size_t other1 = 0; other1 < g1.size(); ++other1) {
            if (g1.has_edge(u, other1)) {
                int other2 = core1[other1];
                if (other2 != -1 && !g2.has_edge(v, static_cast<size_t>(other2))) {
                    return false;
                }
            }
        }
        for (size_t other2 = 0; other2 < g2.size(); ++other2) {
            if (g2.has_edge(v, other2)) {
                int other1 = core2[other2];
                if (other1 != -1 && !g1.has_edge(u, static_cast<size_t>(other1))) {
                    return false;
                }
            }
        }
        return true;
    }

    static bool match(const Graph& g1, const Graph& g2,
                      std::vector<int>& core1,
                      std::vector<int>& core2,
                      size_t depth) {
        if (depth == g1.size()) return true;

        int u = -1;
        for (size_t i = 0; i < g1.size(); ++i) {
            if (core1[i] == -1) {
                u = static_cast<int>(i);
                break;
            }
        }

        for (size_t v = 0; v < g2.size(); ++v) {
            if (core2[v] == -1) {
                if (is_feasible(g1, g2, core1, core2, static_cast<size_t>(u), v)) {
                    core1[u] = static_cast<int>(v);
                    core2[v] = u;

                    if (match(g1, g2, core1, core2, depth + 1)) return true;

                    core1[u] = -1;
                    core2[v] = -1;
                }
            }
        }
        return false;
    }
};

int main() {
    Graph g1(4);
    g1.add_edge(0, 1);
    g1.add_edge(1, 2);
    g1.add_edge(2, 3);
    g1.add_edge(3, 0);

    Graph g2(4);
    g2.add_edge(2, 3);
    g2.add_edge(3, 0);
    g2.add_edge(0, 1);
    g2.add_edge(1, 2);

    auto result = VF2Matcher::find_isomorphism(g1, g2);
    if (result) {
        std::cout << "Графи ізоморфні! Мапінг:\n";
        for (size_t i = 0; i < result->size(); ++i) {
            std::cout << "  G1[" << i << "] -> G2[" << (*result)[i] << "]\n";
        }
    } else {
        std::cout << "Графи не ізоморфні.\n";
    }

    return 0;
}
