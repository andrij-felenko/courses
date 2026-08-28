#include <iostream>

int main() {
    // Двочастковий граф: рядок i — ліва вершина, стовпець j — права; 1 ⟺ є ребро.
    std::vector<std::vector<long long>> A = {
        {1, 1, 0},
        {0, 1, 1},
        {1, 0, 1},
    };
    std::cout << perm_naive(A) << '\n';   // 2
    std::cout << perm_ryser(A) << '\n';   // 2 — стільки ж досконалих паросполучень

    std::vector<std::vector<long long>> J = {   // повний граф K₃,₃ — усі ребра є
        {1, 1, 1},
        {1, 1, 1},
        {1, 1, 1},
    };
    std::cout << perm_ryser(J) << '\n';   // 6 = 3! досконалих паросполучень K₃,₃
    return 0;
}
