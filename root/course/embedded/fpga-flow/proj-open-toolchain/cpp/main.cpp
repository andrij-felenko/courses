#include <cmath>
#include <random>
#include <utility>
#include <vector>

// вартість розкладки: сумарна довжина дротів + штраф за таймінг
double cost(const std::vector<int>& place);

// place[вузол] = номер плитки, у якій той вузол сидить
void anneal_place(std::vector<int>& place) {
    std::mt19937 rng{42};                          // фіксований seed → відтворюваність
    std::uniform_int_distribution<int> node(0, (int)place.size() - 1);
    std::uniform_real_distribution<double> unit(0.0, 1.0);

    double T = 100.0;                              // «температура»: дозвіл на погіршення
    double c = cost(place);                        // тримаємо поточну вартість

    while (T > 0.01) {                             // поки не охололо
        for (int i = 0; i < 100 * (int)place.size(); ++i) {
            int a = node(rng), b = node(rng);      // два випадкові вузли
            std::swap(place[a], place[b]);         // пробний обмін плиток

            double delta = cost(place) - c;        // Δ = вартість_після − до

            // Δ<0 — стало краще, беремо завжди; гірше — інколи, з e^(−Δ/T)
            if (delta < 0.0 || unit(rng) < std::exp(-delta / T))
                c += delta;                        // swap лишається
            else
                std::swap(place[a], place[b]);     // відкат
        }
        T *= 0.95;                                 // повільно остудити (α ≈ 0.95)
    }
    // далі — трасувати дроти між плитками
}
