// Ідіоматична реалізація DFS топологічного сортування мовою C++17.
#include <vector>
#include <algorithm>
#include <optional>

enum class NodeColor { White, Gray, Black };

bool dfsVisit(
    int u, 
    const std::vector<std::vector<int>>& adj, 
    std::vector<NodeColor>& color, 
    std::vector<int>& finishOrder) 
{
    color[u] = NodeColor::Gray;

    for (int v : adj[u]) {
        if (color[v] == NodeColor::Gray) {
            return false; // Знайдено цикл
        }
        if (color[v] == NodeColor::White) {
            if (!dfsVisit(v, adj, color, finishOrder)) {
                return false;
            }
        }
    }

    color[u] = NodeColor::Black;
    finishOrder.push_back(u);
    return true;
}

std::optional<std::vector<int>> dfsTopologicalSort(
    int numNodes, 
    const std::vector<std::vector<int>>& adj) 
{
    std::vector<NodeColor> color(numNodes, NodeColor::White);
    std::vector<int> finishOrder;
    finishOrder.reserve(numNodes);

    for (int i = 0; i < numNodes; ++i) {
        if (color[i] == NodeColor::White) {
            if (!dfsVisit(i, adj, color, finishOrder)) {
                return std::nullopt; // Знайдено цикл
            }
        }
    }

    // Розвертаємо post-order порядок
    std::reverse(finishOrder.begin(), finishOrder.end());
    return finishOrder;
}
