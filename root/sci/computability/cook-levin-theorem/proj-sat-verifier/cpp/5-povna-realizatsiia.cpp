// Generator & Verifier of Cook-Levin CNF Formulas in C++ (C++20)
#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <array>
#include <optional>
#include <fstream>
#include <format>

struct Transition {
    int next_state;
    int next_symbol;
    int direction; // +1 R, -1 L, 0 Stay
};

class TuringMachine {
public:
    int num_states;
    int num_alphabet;
    int q0;
    int q_accept;

    TuringMachine(int states, int alphabet, int start, int accept)
        : num_states(states), num_alphabet(alphabet), q0(start), q_accept(accept) {
        transitions.resize(states, std::vector<std::optional<Transition>>(alphabet, std::nullopt));
    }

    void set_transition(int q, int sym, int next_q, int next_sym, int dir) {
        transitions[q][sym] = Transition{next_q, next_sym, dir};
    }

    [[nodiscard]] std::optional<Transition> get_transition(int q, int sym) const {
        return transitions[q][sym];
    }

private:
    std::vector<std::vector<std::optional<Transition>>> transitions;
};

class CookLevinCNFGenerator {
public:
    CookLevinCNFGenerator(const TuringMachine& tm, int time_steps)
        : tm_(tm), time_steps_(time_steps), tape_size_(time_steps + 1) {
        vars_per_cell_ = tm_.num_alphabet + tm_.num_states;
        total_vars_ = (time_steps_ + 1) * tape_size_ * vars_per_cell_;
    }

    [[nodiscard]] int get_x_var(int t, int j, int sym) const noexcept {
        int cell_idx = t * tape_size_ + j;
        return cell_idx * vars_per_cell_ + sym + 1;
    }

    [[nodiscard]] int get_y_var(int t, int j, int q) const noexcept {
        int cell_idx = t * tape_size_ + j;
        return cell_idx * vars_per_cell_ + tm_.num_alphabet + q + 1;
    }

    void generate_dimacs(std::ostream& out, std::span<const int> input_string) const {
        std::vector<std::string> clauses;

        // 1. Cell uniqueness & presence constraints
        for (int t = 0; t <= time_steps_; ++t) {
            for (int j = 0; j < tape_size_; ++j) {
                std::string cell_presence;
                for (int s = 0; s < tm_.num_alphabet; ++s) {
                    cell_presence += std::to_string(get_x_var(t, j, s)) + " ";
                }
                clauses.push_back(cell_presence + "0");

                for (int s1 = 0; s1 < tm_.num_alphabet; ++s1) {
                    for (int s2 = s1 + 1; s2 < tm_.num_alphabet; ++s2) {
                        clauses.push_back(std::format("-{} -{} 0", get_x_var(t, j, s1), get_x_var(t, j, s2)));
                    }
                }
            }
        }

        // 2. Start configuration
        clauses.push_back(std::format("{} 0", get_y_var(0, 0, tm_.q0)));
        for (size_t j = 0; j < input_string.size(); ++j) {
            clauses.push_back(std::format("{} 0", get_x_var(0, static_cast<int>(j), input_string[j])));
        }

        // 3. Accept state condition
        std::string accept_clause;
        for (int t = 0; t <= time_steps_; ++t) {
            for (int j = 0; j < tape_size_; ++j) {
                accept_clause += std::to_string(get_y_var(t, j, tm_.q_accept)) + " ";
            }
        }
        clauses.push_back(accept_clause + "0");

        // Print DIMACS Header
        out << std::format("c Cook-Levin SAT Formula Generator in C++\n");
        out << std::format("p cnf {} {}\n", total_vars_, clauses.size());
        for (const auto& clause : clauses) {
            out << clause << "\n";
        }
    }

private:
    const TuringMachine& tm_;
    int time_steps_;
    int tape_size_;
    int vars_per_cell_;
    int total_vars_;
};

int main() {
    TuringMachine tm(3, 3, 0, 2);
    tm.set_transition(0, 0, 1, 1, +1);
    tm.set_transition(1, 1, 2, 1, +1);

    CookLevinCNFGenerator generator(tm, 2);
    std::array<int, 2> input = {0, 1};

    generator.generate_dimacs(std::cout, input);
    return 0;
}
