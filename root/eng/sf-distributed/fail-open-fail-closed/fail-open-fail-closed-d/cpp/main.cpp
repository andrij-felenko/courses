#include <iostream>
#include <iomanip>

struct CostEvaluation {
    double alpha;          // Частка зловмисників / невалідного трафіку (0.0 - 1.0)
    double cost_downtime;  // Вартість втрати одного легітимного запиту ($)
    double cost_breach;    // Вартість пропуску одного зловмисного запиту ($)

    double critical_alpha() const {
        return cost_downtime / (cost_downtime + cost_breach);
    }

    bool should_fail_open() const {
        return alpha < critical_alpha();
    }
};

int main() {
    // Сценарій 1: Публічний блог / рекомендації
    // Простій коштує $0.05 на запит (реклама), пропуск спам-коментаря коштує $0.10
    CostEvaluation blog{.alpha = 0.01, .cost_downtime = 0.05, .cost_breach = 0.10};

    // Сценарій 2: Банківський переказ
    // Простій коштує $2.00 (SLA), пропуск несанкціонованого списання коштує $5000.00
    CostEvaluation banking{.alpha = 0.001, .cost_downtime = 2.00, .cost_breach = 5000.00};

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "Блог: поріг alpha = " << blog.critical_alpha() 
              << " -> Режим: " << (blog.should_fail_open() ? "FAIL-OPEN" : "FAIL-CLOSED") << "\n";
    std::cout << "Банк: поріг alpha = " << banking.critical_alpha() 
              << " -> Режим: " << (banking.should_fail_open() ? "FAIL-OPEN" : "FAIL-CLOSED") << "\n";
    return 0;
}
