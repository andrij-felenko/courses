#include <optional>
#include <functional>
#include <algorithm>

enum Color { WHITE, GRAY, BLACK };

std::optional<std::vector<std::string>> find_cycle(const Graph& g) {
    std::unordered_map<std::string, Color> color;
    for (const auto& [u, _] : g) color[u] = WHITE;
    std::unordered_map<std::string, std::string> parent;

    std::function<std::optional<std::vector<std::string>>(const std::string&)> walk =
        [&](const std::string& u) -> std::optional<std::vector<std::string>> {
        color[u] = GRAY;                              // u зайшов у стек обходу
        std::vector<std::string> nbrs(g.at(u).begin(), g.at(u).end());
        std::sort(nbrs.begin(), nbrs.end());          // детермінований звіт
        for (const auto& v : nbrs) {
            if (color[v] == GRAY) {                   // ребро у СІРЕ = замкнення назад
                std::vector<std::string> path{u};
                while (path.back() != v)              // підіймаємось по батьках u → … → v
                    path.push_back(parent[path.back()]);
                std::reverse(path.begin(), path.end());  // тепер v → … → u
                path.push_back(v);                    // ребро u → v замикає цикл
                return path;
            }
            if (color[v] == WHITE) {
                parent[v] = u;
                if (auto found = walk(v)) return found;
            }
        }
        color[u] = BLACK;                             // u й усе під ним оброблено
        return std::nullopt;
    };

    for (const auto& [u, _] : g)
        if (color[u] == WHITE)
            if (auto found = walk(u)) return found;    // напр. {"orders","report","orders"}
    return std::nullopt;
}
