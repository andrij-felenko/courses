// Лексикографічне топологічне сортування мовою C++ (використовує std::priority_queue).
#include <vector>
#include <queue>
#include <optional>

std::optional<std::vector<int>> lexicographicalTopologicalSort(
    int numNodes, 
    const std::vector<std::vector<int>>& adj) 
{
    std::vector<int> inDegree(numNodes, 0);
    for (int u = 0; u < numNodes; ++u) {
        for (int v : adj[u]) {
            inDegree[v]++;
        }
    }

    // Min-Heap: найменший елемент завжди нагорі
    std::priority_queue<int, std::vector<int>, std::greater<int>> minHeap;
    for (int i = 0; i < numNodes; ++i) {
        if (inDegree[i] == 0) {
            minHeap.push(i);
        }
    }

    std::vector<int> result;
    result.reserve(numNodes);

    while (!minHeap.empty()) {
        int u = minHeap.top();
        minHeap.pop();
        result.push_back(u);

        for (int v : adj[u]) {
            if (--inDegree[v] == 0) {
                minHeap.push(v);
            }
        }
    }

    if (static_cast<int>(result.size()) != numNodes) {
        return std::nullopt; // Знайдено цикл
    }

    return result;
}
