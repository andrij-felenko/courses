#include <iostream>
#include <vector>
#include <stack>
#include <memory>

enum class Color { White, Gray, Black };

class Graph {
private:
    std::size_t vertices_;
    std::vector<std::vector<int>> adj_;

public:
    explicit Graph(std::size_t vertices) 
        : vertices_(vertices), adj_(vertices) {}

    void add_edge(int u, int v) {
        adj_.at(u).push_back(v);
    }

    [[nodiscard]] std::size_t num_vertices() const noexcept {
        return vertices_;
    }

    [[nodiscard]] const std::vector<int>& neighbors(int u) const {
        return adj_.at(u);
    }
};

struct DFSResult {
    std::vector<int> discovery_time;
    std::vector<int> finish_time;
    std::vector<int> parent;
    bool has_cycle{false};
};

class DFSSolver {
public:
    static DFSResult run_recursive(const Graph& g) {
        const std::size_t n = g.num_vertices();
        DFSResult res;
        res.discovery_time.resize(n, 0);
        res.finish_time.resize(n, 0);
        res.parent.resize(n, -1);

        std::vector<Color> color(n, Color::White);
        int timer = 0;

        auto visit = [&](auto& self, int u) -> void {
            color[u] = Color::Gray;
            res.discovery_time[u] = ++timer;

            for (int v : g.neighbors(u)) {
                if (color[v] == Color::White) {
                    res.parent[v] = u;
                    self(self, v);
                } else if (color[v] == Color::Gray) {
                    res.has_cycle = true;
                }
            }

            color[u] = Color::Black;
            res.finish_time[u] = ++timer;
        };

        for (std::size_t i = 0; i < n; ++i) {
            if (color[i] == Color::White) {
                visit(visit, static_cast<int>(i));
            }
        }

        return res;
    }
};
