int main() {
    std::cout << "=== Демонстрація розв'язання рівняння Пелля ===\n";
    constexpr uint64_t d = 61;
    if (auto fund = PellSolver::find_fundamental(d)) {
        std::cout << "Фундаментальний розв'язок для D = " << d << ":\n"
                  << "  x₁ = " << fund->to_string_x() << "\n"
                  << "  y₁ = " << fund->to_string_y() << "\n";

        auto sol2 = PellSolver::next_power(*fund, *fund, d);
        std::cout << "Другий розв'язок (x₂, y₂):\n"
                  << "  x₂ = " << sol2.to_string_x() << "\n"
                  << "  y₂ = " << sol2.to_string_y() << "\n";
    }

    std::cout << "\n=== Довблення гіперкуба (Пошук піфагорової трійки) ===\n";
    auto pythagoras = [](std::span<const int64_t> v) -> int64_t {
        const int64_t x = v[0], y = v[1], z = v[2];
        if (x == 0 || y == 0 || z == 0) return -1;
        return (x * x + y * y - z * z) * (x * x + y * y - z * z) + (x - 3) * (x - 3);
    };

    if (!ModularSieve::has_local_solution(pythagoras, 3, 4)) {
        std::cout << "Рівняння відхилено модульним ситом за модулем 4.\n";
    } else {
        std::cout << "Модульне сито пройдено успішно. Запуск довблення...\n";
        DiophantineSolver solver(pythagoras, 3);
        SearchProfile stats;
        if (auto sol = solver.search(10, stats)) {
            std::cout << "Знайдено розв'язок: x=" << (*sol)[0] 
                      << ", y=" << (*sol)[1] 
                      << ", z=" << (*sol)[2]
                      << " (Оцінено точок: " << stats.evaluated_points << ")\n";
        }
    }

    return 0;
}
