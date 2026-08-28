#include <string>
#include <vector>
#include <utility>
#include <unordered_map>
#include <unordered_set>

using Graph = std::unordered_map<std::string, std::unordered_set<std::string>>;

// граф: модуль → модулі, від яких він ПРЯМО залежить
Graph build_graph(const std::vector<std::pair<std::string, std::string>>& edges) {
    Graph g;
    for (const auto& [src, dst] : edges) {
        g[src];                               // вузол існує навіть без вихідних ребер
        g[dst];
        if (src != dst)                       // самопосилання модуля на себе — не ребро
            g[src].insert(dst);
    }
    return g;
}
