#include <iostream>
#include <mathieu/solver.hpp>

int main() {
    using namespace mathieu::solver;

    // Створення розв'язувача з підвищеною точністю RK4 (2000 кроків за період)
    Config config;
    config.period_steps = 2000;
    MathieuSolver solver(config);

    // Робочі параметри пастки Поля: a = 0.237, q = 0.706
    double a_paul = 0.237;
    double q_paul = 0.706;

    PointResult res = solver.analyze_point(a_paul, q_paul);

    std::cout << "Аналіз робочої точки іонної пастки Поля:\n";
    std::cout << "Слід монодромії Tr(M): " << res.trace << "\n";
    
    if (res.state == StabilityState::Stable) {
        std::cout << "Статус: СТІЙКИЙ РЕЖИМ (Іон утримується в пастці)\n";
        std::cout << "Частота мікроколивань nu: " << res.floquet_nu << "\n";
    } else {
        std::cout << "Статус: НЕСТІЙКИЙ РЕЖИМ (Іон вилітає на електроди!)\n";
        std::cout << "Показник вильоту (μ): " << res.floquet_exponent << "\n";
    }

    return 0;
}
