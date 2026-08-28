#include <iostream>
#include <vector>
#include <numeric>
#include <map>

// Структура для підтримки класів еквівалентності
class EquivalencePartitioner {
private:
    std::vector<int> parent;
    std::vector<int> rank;

public:
    // Ініціалізація: N елементів, кожен є своїм власним класом
    EquivalencePartitioner(int n) {
        parent.resize(n);
        rank.assign(n, 0);
        // Кожен елемент спочатку вказує сам на себе (рефлексивність)
        std::iota(parent.begin(), parent.end(), 0);
    }

    // Операція Find: знаходить "представника" класу для елемента i
    // Використовує евристику "стиснення шляху" (path compression)
    int find_representative(int i) {
        if (parent[i] == i) {
            return i;
        }
        // Рекурсивний пошук кореня з одночасним перепідключенням напряму до кореня
        parent[i] = find_representative(parent[i]);
        return parent[i];
    }

    // Операція Union: об'єднує класи двох елементів (встановлює відношення u ≡ v)
    void add_relation(int u, int v) {
        int root_u = find_representative(u);
        int root_v = find_representative(v);

        if (root_u != root_v) {
            // Евристика "об'єднання за рангом" (union by rank)
            if (rank[root_u] < rank[root_v]) {
                parent[root_u] = root_v;
            } else if (rank[root_u] > rank[root_v]) {
                parent[root_v] = root_u;
            } else {
                parent[root_v] = root_u;
                rank[root_u]++;
            }
        }
    }
};
