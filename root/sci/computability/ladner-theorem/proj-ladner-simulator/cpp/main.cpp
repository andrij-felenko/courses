#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <functional>
#include <optional>

// Ідіоматичний C++20 клас симулятора Леднера
class LadnerSimulator {
public:
    using MachineFunc = std::function<bool(std::string_view)>;
    using ReductionFunc = std::function<std::string(std::string_view)>;

    struct StepResult {
        int h_value{0};
        std::size_t steps_used{0};
        bool phase_switched{false};
        std::string counterexample{};
    };

    explicit LadnerSimulator(MachineFunc machine, ReductionFunc reduction)
        : m_machine(std::move(machine)), m_reduction(std::move(reduction)) {}

    // Оцінка мови SAT за канонічною моделлю
    [[nodiscard]] static bool oracle_sat(std::string_view input) noexcept {
        if (input.empty()) return false;
        std::size_t sum = 0;
        for (char c : input) {
            sum += static_cast<unsigned char>(c);
        }
        return (sum % 2 == 0);
    }

    // Мова Леднера A(x)
    [[nodiscard]] static bool eval_ladner_language(std::string_view input, int h_val) noexcept {
        if (h_val % 2 != 0) {
            return false; // Непарна фаза: порожня мова
        }
        return oracle_sat(input);
    }

    // Виконання симуляційного кроку з контролем часового бюджету n^3
    [[nodiscard]] StepResult run_step(int n, int prev_h) const {
        StepResult res{.h_value = prev_h};
        const std::size_t budget = static_cast<std::size_t>(n * n * n);

        if (prev_h % 2 == 0) {
            // Парна фаза: спростування P (машини M_i)
            for (int len = 1; len <= n; ++len) {
                std::string test_input = "test_str_" + std::to_string(len);
                
                bool m_out = m_machine(test_input);
                bool true_a = eval_ladner_language(test_input, prev_h);
                
                res.steps_used += static_cast<std::size_t>(len * len);
                if (res.steps_used > budget) break;

                if (m_out != true_a) {
                    res.h_value = prev_h + 1;
                    res.phase_switched = true;
                    res.counterexample = test_input;
                    return res;
                }
            }
        } else {
            // Непарна фаза: спростування NP-повноти (зведення R_i)
            for (int len = 1; len <= n; ++len) {
                std::string test_input = "sat_formula_" + std::to_string(len);
                
                std::string red_target = m_reduction(test_input);
                bool is_sat = oracle_sat(test_input);
                bool target_in_a = eval_ladner_language(red_target, prev_h);

                res.steps_used += static_cast<std::size_t>(len * len);
                if (res.steps_used > budget) break;

                if (is_sat != target_in_a) {
                    res.h_value = prev_h + 1;
                    res.phase_switched = true;
                    res.counterexample = test_input;
                    return res;
                }
            }
        }

        return res;
    }

private:
    MachineFunc m_machine;
    ReductionFunc m_reduction;
};

int main() {
    std::cout << "=== ДІАГНОСТИЧНИЙ СИМУЛЯТОР ЛЕДНЕРА (C++20) ===\n";

    // Створюємо хибну машину та хибне зведення
    auto dummy_machine = [](std::string_view) -> bool { return true; };
    auto dummy_reduction = [](std::string_view) -> std::string { return ""; };

    LadnerSimulator simulator(dummy_machine, dummy_reduction);
    int current_h = 0;

    for (int n = 1; n <= 10; ++n) {
        auto res = simulator.run_step(n, current_h);
        
        std::cout << "n = " << n 
                  << " | Бюджет = " << (n * n * n) 
                  << " | Кроки = " << res.steps_used 
                  << " | H(n) = " << res.h_value;

        if (res.phase_switched) {
            std::cout << " -> [ПЕРЕКЛЮЧЕННЯ! Контрекземпляр: " << res.counterexample << "]";
        }
        std::cout << '\n';

        current_h = res.h_value;
    }

    return 0;
}
