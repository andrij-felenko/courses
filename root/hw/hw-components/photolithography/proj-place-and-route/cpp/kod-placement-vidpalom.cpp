#include <vector>
#include <random>
#include <cmath>
#include <algorithm>
#include <climits>

struct Cell { int row, col; };            // позиція комірки у сітці рядків
struct Net  { std::vector<int> cells; };  // ланцюг: індекси з'єднаних комірок

// HPWL (half-perimeter wirelength) — півпериметр обгортувального
// прямокутника ланцюга: ширина + висота. Стандартна оцінка довжини дротів.
long hpwl(const Net& net, const std::vector<Cell>& c) {
    int minR = INT_MAX, maxR = INT_MIN, minC = INT_MAX, maxC = INT_MIN;
    for (int id : net.cells) {
        minR = std::min(minR, c[id].row);  maxR = std::max(maxR, c[id].row);
        minC = std::min(minC, c[id].col);  maxC = std::max(maxC, c[id].col);
    }
    return (maxR - minR) + (maxC - minC);
}

long totalCost(const std::vector<Net>& nets, const std::vector<Cell>& c) {
    long sum = 0;
    for (const Net& n : nets) sum += hpwl(n, c);
    return sum;
}

// Розкладка імітованим відпалом: обмінюємо пари комірок місцями,
// приймаємо кожен хід, що коротшає дроти, і зрідка — гірший,
// щоб не застрягнути в поганому локальному мінімумі.
void placeAnneal(std::vector<Cell>& c, const std::vector<Net>& nets) {
    std::mt19937 rng(1);
    std::uniform_int_distribution<int> pick(0, static_cast<int>(c.size()) - 1);
    std::uniform_real_distribution<double> coin(0.0, 1.0);

    long cost = totalCost(nets, c);
    for (double T = 100.0; T > 0.01; T *= 0.995) {   // повільне охолодження
        int a = pick(rng), b = pick(rng);
        if (a == b) continue;
        std::swap(c[a], c[b]);                        // локальний хід: обмін місцями
        long delta = totalCost(nets, c) - cost;
        if (delta <= 0 || coin(rng) < std::exp(-delta / T))
            cost += delta;                            // кращий — лишаємо; гірший — інколи
        else
            std::swap(c[a], c[b]);                    // відкат ходу
    }
}
