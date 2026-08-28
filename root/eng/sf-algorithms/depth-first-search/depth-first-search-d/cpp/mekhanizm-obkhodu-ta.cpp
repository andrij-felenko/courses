#include <vector>
#include <cstdint>

enum class Color : std::uint8_t { White, Gray, Black };

class Graph {
public:
    explicit Graph(std::size_t n) : adj_(n) {}
    void add_edge(int u, int v) { adj_[u].push_back(v); }
    [[nodiscard]] std::size_t num_vertices() const noexcept { return adj_.size(); }
    [[nodiscard]] const std::vector<int>& neighbors(int u) const { return adj_[u]; }
private:
    std::vector<std::vector<int>> adj_;
};

void dfs_visit(const Graph& g, int u, std::vector<Color>& color,
               std::vector<int>& d, std::vector<int>& f, int& timer) {
    color[u] = Color::Gray;     // 1. Вхід у вершину: позначаємо активною
    d[u] = ++timer;             // 2. Фіксуємо час відкриття

    for (int v : g.neighbors(u)) {
        if (color[v] == Color::White) { // Якщо сусід білий — занурюємося вглиб
            dfs_visit(g, v, color, d, f, timer);
        }
    }

    color[u] = Color::Black;    // 3. Завершення вершини
    f[u] = ++timer;             // 4. Фіксуємо час завершення
}
