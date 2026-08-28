// Нерекурсивна (ітеративна) реалізація DFS топологічного сортування мовою C++.
// Абсолютно безпечна до глибини рекурсії та переповнення стеку.
#include <vector>
#include <algorithm>
#include <optional>

std::optional<std::vector<int>> iterativeDfsTopologicalSort(
    int numNodes, 
    const std::vector<std::vector<int>>& adj) 
{
    std::vector<int> color(numNodes, 0); // 0: White, 1: Gray, 2: Black
    std::vector<int> edgeIndex(numNodes, 0); // Поточний індекс ребра для кожної вершини
    std::vector<int> finishOrder;
    finishOrder.reserve(numNodes);

    std::vector<int> stack;

    for (int startNode = 0; startNode < numNodes; ++startNode) {
        if (color[startNode] != 0) continue;

        stack.push_back(startNode);
        color[startNode] = 1; // Gray

        while (!stack.empty()) {
            int u = stack.back();

            if (edgeIndex[u] < static_cast<int>(adj[u].size())) {
                int v = adj[u][edgeIndex[u]++];

                if (color[v] == 1) {
                    return std::nullopt; // Цикл знайдено (зворотне ребро у Gray)
                }
                if (color[v] == 0) {
                    color[v] = 1; // Gray
                    stack.push_back(v);
                }
            } else {
                // Усі сусіди u оброблені
                color[u] = 2; // Black
                finishOrder.push_back(u);
                stack.pop_back();
            }
        }
    }

    std::reverse(finishOrder.begin(), finishOrder.end());
    return finishOrder;
}
