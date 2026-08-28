#include <iostream>
#include <vector>
#include <algorithm>
#include <utility>

// Компонент 1: Перевірка на простоту
// Використовується для визначення, чи є частка двох дільників простим числом.
bool is_prime(int n) {
    if (n < 2) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0)
            return false;
    }
    return true;
}

// Компонент 2: Знаходження всіх дільників
// Шукаємо дільники за O(√n) і сортуємо їх за зростанням.
std::vector<int> get_divisors(int n) {
    std::vector<int> divs;
    for (int i = 1; i * i <= n; ++i) {
        if (n % i == 0) {
            divs.push_back(i);
            if (i * i != n) {
                divs.push_back(n / i);
            }
        }
    }
    std::sort(divs.begin(), divs.end());
    return divs;
}

// Компонент 3: Генерація ребер діаграми Хассе
// Для кожної пари дільників a і b (де a < b) перевіряємо, 
// чи ділить a число b, і чи є їхня частка b/a простим числом.
std::vector<std::pair<int, int>> generate_hasse_edges(const std::vector<int>& divs) {
    std::vector<std::pair<int, int>> edges;
    for (size_t i = 0; i < divs.size(); ++i) {
        for (size_t j = i + 1; j < divs.size(); ++j) {
            int a = divs[i];
            int b = divs[j];
            if (b % a == 0 && is_prime(b / a)) {
                edges.push_back({a, b});
            }
        }
    }
    return edges;
}

// Компонент 4: Вивід графа (ребер)
// Друкує результат у форматі, зручному для побудови графів (наприклад, Graphviz).
void print_graph(int n, const std::vector<std::pair<int, int>>& edges) {
    std::cout << "digraph D_" << n << " {\n";
    std::cout << "  rankdir=BT;\n"; // Знизу вгору
    for (const auto& edge : edges) {
        std::cout << "  " << edge.first << " -> " << edge.second << ";\n";
    }
    std::cout << "}\n";
}

// Компонент 5: Головна функція
int main() {
    int n = 36; // Можна змінити на будь-яке інше число
    std::cout << "// Генерація решітки дільників для n = " << n << "\n";
    
    std::vector<int> divisors = get_divisors(n);
    std::vector<std::pair<int, int>> hasse_edges = generate_hasse_edges(divisors);
    
    print_graph(n, hasse_edges);
    
    return 0;
}
