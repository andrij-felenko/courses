#include <iostream>
#include <vector>
#include <chrono>

class NQueensBitmask {
private:
    int n;
    int limit; // Маска з N одиниць в молодших бітах
    long long solutionCount;

    void solve(int cols, int diag1, int diag2) {
        // Якщо всі стовпчики заповнені, ми досягли мети (листок дерева розв'язків)
        if (cols == limit) {
            solutionCount++;
            return;
        }

        // Обчислюємо маску доступних позицій у поточному рядку
        int pos = limit & ~(cols | diag1 | diag2);

        // Поки є доступні позиції для розміщення ферзя
        while (pos > 0) {
            // Отримуємо наймолодший встановлений 1-біт (найпершу вільну клітинку)
            int bit = pos & -pos;

            // Виключаємо вибрану клітинку з маски доступних позицій
            pos -= bit;

            // Рекурсивний перехід на наступний рядок із оновленням масок діагоналей
            solve(cols | bit, (diag1 | bit) << 1, (diag2 | bit) >> 1);
        }
    }

public:
    explicit NQueensBitmask(int boardSize) : n(boardSize), solutionCount(0) {
        // Наприклад, для N = 8: limit = (1 << 8) - 1 = 11111111 в двійковій системі
        limit = (1 << n) - 1;
    }

    long long countSolutions() {
        solutionCount = 0;
        solve(0, 0, 0);
        return solutionCount;
    }
};

int main() {
    int n = 12;
    NQueensBitmask solver(n);
    
    auto start = std::chrono::high_resolution_clock::now();
    long long count = solver.countSolutions();
    auto end = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double, std::milli> elapsed = end - start;

    std::cout << "Кількість розв'язків для " << n << "-Ферзів: " << count << "\n";
    std::cout << "Час виконання: " << elapsed.count() << " мс\n";
    return 0;
}
