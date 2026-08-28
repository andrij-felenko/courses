// Приклад паралельного збору перерізів Пуанкаре для сітки параметрів у C++20
#include <execution>
#include <algorithm>

void run_parallel_sweep(std::span<const double> frequencies) {
    std::vector<std::vector<poincare::SectionPoint<2>>> results(frequencies.size());

    std::transform(std::execution::par, 
                   frequencies.begin(), frequencies.end(), 
                   results.begin(),
                   [](double omega) {
                       auto sys = [omega](const std::array<double,2>& s, double t, std::array<double,2>& out) {
                           out[0] = s[1];
                           out[1] = -0.2 * s[1] + s[0] - s[0]*s[0]*s[0] + 0.3 * std::cos(omega * t);
                       };
                       auto sec = [](const std::array<double,2>& s, std::array<double,2>& grad) {
                           grad = {0.0, 1.0};
                           return s[1]; // Sekuchiy peretyn v = 0
                       };
                       poincare::MapSolver<2, decltype(sys), decltype(sec)> solver(sys, sec);
                       auto res = solver.compute_series({0.1, 0.0}, 100);
                       return res ? *res : std::vector<poincare::SectionPoint<2>>{};
                   });
}
