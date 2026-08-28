#include "cantor.hpp"
#include <iostream>
#include <vector>

int main() {
    try {
        using namespace math::fractals;

        std::cout << "=== Інтеграційний тест бібліотеки libcantor ===\n";

        // 1. Створення та генерація Канторової множини 6-го рівня
        CantorSet cantor(6);
        std::cout << "Успішно згенеровано " << cantor.size() << " інтервалів.\n";

        // 2. Оцінка вимірності методом Box-Counting
        CantorAnalyzer analyzer(cantor);
        const auto result = analyzer.compute_box_counting();

        std::cout << "Обчислена вимірність: " << result.box_counting_dim << "\n";
        std::cout << "Середньоквадратична похибка регресії: " << result.mean_squared_error << "\n";

        // 3. Сканування точок фазового простору
        const std::vector<double> test_points{0.0, 0.25, 1.0 / 3.0, 0.5, 0.75, 1.0};
        std::cout << "\nПеревірка належності точок (глибина 25):\n";
        for (double pt : test_points) {
            const bool inside = CantorSet::contains(pt, 25);
            std::cout << "  x = " << pt << " -> " << (inside ? "C (Належить)" : "U (Вилучено)") << "\n";
        }

        // 4. Обчислення значення функції Кантора ("Диявольських сходів")
        const double x_val = 0.4;
        const double staircase_val = CantorSet::evaluate_staircase(x_val);
        std::cout << "\nЗначення функції Кантора F(" << x_val << ") = " << staircase_val << "\n";

    } catch (const math::fractals::CantorException& ex) {
        std::cerr << "Критична помилка CantorLib: " << ex.what() << " (код статусу: " << static_cast<int>(ex.status()) << ")\n";
        return 1;
    } catch (const std::exception& ex) {
        std::cerr << "Системний виняток: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
