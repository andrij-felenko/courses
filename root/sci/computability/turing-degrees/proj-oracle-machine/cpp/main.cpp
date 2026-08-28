#include <iostream>
#include <vector>
#include <unordered_set>
#include <memory>
#include <optional>
#include <string_view>
#include <algorithm>
#include <cstdint>

// --- Об'єктно-орієнтований симулятор на C++20 ---

class FiniteOracle {
private:
    std::unordered_set<uint32_t> elements_;

public:
    explicit FiniteOracle(std::initializer_list<uint32_t> init) : elements_(init) {}

    void insert(uint32_t val) { elements_.insert(val); }
    void remove(uint32_t val) { elements_.erase(val); }

    [[nodiscard]] bool contains(uint32_t val) const noexcept {
        return elements_.contains(val);
    }
};

struct QueryRecord {
    uint32_t queried_value;
    bool response;
};

class QueryTracker {
private:
    std::vector<QueryRecord> history_;
    uint32_t max_queried_{0};

public:
    bool query(const FiniteOracle& oracle, uint32_t val) {
        bool res = oracle.contains(val);
        history_.push_back({val, res});
        max_queried_ = std::max(max_queried_, val);
        return res;
    }

    [[nodiscard]] uint32_t get_use_function() const noexcept {
        return history_.empty() ? 0 : max_queried_ + 1;
    }

    [[nodiscard]] const std::vector<QueryRecord>& get_history() const noexcept {
        return history_;
    }
};

enum class ExecutionState {
    Running,
    Halted,
    TimeLimitExceeded
};

class OracleTuringMachine {
private:
    std::vector<int> tape_;
    size_t head_position_{512};
    size_t steps_{0};
    ExecutionState state_{ExecutionState::Running};
    QueryTracker tracker_;

public:
    OracleTuringMachine() : tape_(1024, 0) {}

    void run_program(const FiniteOracle& oracle, uint32_t input_x) {
        steps_ = 0;
        state_ = ExecutionState::Running;

        // Крок 1: Запит до оракула про наявність input_x
        steps_++;
        bool answer = tracker_.query(oracle, input_x);

        // Крок 2: Модифікація стрічки залежно від відповіді
        steps_++;
        if (answer) {
            tape_[head_position_] = static_cast<int>(input_x * 2 + 1);
        } else {
            tape_[head_position_] = -1;
        }

        state_ = ExecutionState::Halted;
    }

    [[nodiscard]] ExecutionState get_state() const noexcept { return state_; }
    [[nodiscard]] size_t get_steps() const noexcept { return steps_; }
    [[nodiscard]] const QueryTracker& get_tracker() const noexcept { return tracker_; }
    [[nodiscard]] int get_tape_value() const noexcept { return tape_[head_position_]; }
};

// Моделювання симуляції пріоритету Фрідберга — Мучника
class PriorityMethodSimulator {
private:
    struct Requirement {
        size_t id;
        uint32_t witness;
        bool satisfied{false};
        uint32_t restraint{0};
    };

    std::vector<Requirement> reqs_A_; // Для A != M_e^B
    std::vector<Requirement> reqs_B_; // Для B != M_e^A
    FiniteOracle set_A_{{}};
    FiniteOracle set_B_{{}};

public:
    explicit PriorityMethodSimulator(size_t num_requirements) {
        uint32_t w = 0;
        for (size_t i = 0; i < num_requirements; ++i) {
            reqs_A_.push_back({i, w++, false, 0});
            reqs_B_.push_back({i, w++, false, 0});
        }
    }

    void step_simulate() {
        std::cout << "\n=== Симуляція кроку пріоритету Фрідберга-Мучника ===\n";
        for (size_t i = 0; i < reqs_A_.size(); ++i) {
            auto& req = reqs_A_[i];
            if (!req.satisfied) {
                // Задовольняємо вимогу R_{2e}: додаємо свідок до A
                set_A_.insert(req.witness);
                req.satisfied = true;
                req.restraint = req.witness + 5;
                std::cout << "[Вимога R_" << (2 * i) << "] Задоволена: свідок "
                          << req.witness << " додано до A. Обмеження r = "
                          << req.restraint << "\n";

                // Пошкодження (Injury) вимог нижчого пріоритету в B
                for (size_t j = i + 1; j < reqs_B_.size(); ++j) {
                    if (reqs_B_[j].satisfied && reqs_B_[j].witness < req.restraint) {
                        reqs_B_[j].satisfied = false;
                        std::cout << "  ↳ [ПОШКОДЖЕННЯ] Вимога R_" << (2 * j + 1)
                                  << " пошкоджена обмеженням r=" << req.restraint << "!\n";
                    }
                }
            }
        }
    }
};

int main() {
    FiniteOracle oracle_B{2, 5, 8, 11, 14};
    OracleTuringMachine machine;

    std::cout << "=== Симуляція оракульної машини на C++20 ===\n";
    for (uint32_t x : {2, 3, 5, 7}) {
        machine.run_program(oracle_B, x);
        std::cout << "Вхід x=" << x
                  << " | Стан: " << (machine.get_state() == ExecutionState::Halted ? "Зупинено" : "Працює")
                  << " | Стрічка: " << machine.get_tape_value()
                  << " | Функція використання u(" << x << ") = "
                  << machine.get_tracker().get_use_function() << "\n";
    }

    PriorityMethodSimulator sim(3);
    sim.step_simulate();

    return 0;
}
