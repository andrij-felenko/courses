// Ідіоматична реалізація алгоритму Кана мовою C++ (C++17/C++20).
// Використовує std::vector, std::queue та std::optional для чіткої обробки помилок.
#include <vector>
#include <queue>
#include <optional>
#include <iostream>

std::optional<std::vector<int>> kahnTopologicalSort(
    int numNodes, 
    const std::vector<std::vector<int>>& adj) 
{
    std::vector<int> inDegree(numNodes, 0);

    // 1. Підрахунок вхідних степеней
    for (int u = 0; u < numNodes; ++u) {
        for (int v : adj[u]) {
            inDegree[v]++;
        }
    }

    // 2. Черга джерел (in_degree == 0)
    std::queue<int> zeroInDegreeQueue;
    for (int i = 0; i < numNodes; ++i) {
        if (inDegree[i] == 0) {
            zeroInDegreeQueue.push(i);
        }
    }

    std::vector<int> resultOrder;
    resultOrder.reserve(numNodes);

    // 3. Обробка черги
    while (!zeroInDegreeQueue.empty()) {
        int u = zeroInDegreeQueue.front();
        zeroInDegreeQueue.pop();
        resultOrder.push_back(u);

        for (int v : adj[u]) {
            if (--inDegree[v] == 0) {
                zeroInDegreeQueue.push(v);
            }
        }
    }

    // Якщо додано менше вершин, ніж numNodes — у графі є цикл
    if (static_cast<int>(resultOrder.size()) != numNodes) {
        return std::nullopt; // Сигнал про присутність циклу
    }

    return resultOrder;
}
