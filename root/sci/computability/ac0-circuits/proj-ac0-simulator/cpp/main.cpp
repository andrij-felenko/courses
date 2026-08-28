// cpp — Ідіоматичний C++20 симулятор схем AC0 з RAII, std::variant та std::span
#include <iostream>
#include <vector>
#include <memory>
#include <random>
#include <variant>
#include <span >
#include <stdexcept>
#include <numeric>

enum class GateType { Input, Not, And, Or };

struct Gate {
    size_t id;
    GateType type;
    size_t input_var_idx{0};
    std::vector<size_t> fan_in;
    mutable uint8_t cached_value{0};
};

enum class VariableState { Zero = 0, One = 1, Free = -1 };

class AC0Circuit {
public:
    explicit AC0Circuit(size_t num_inputs) : num_inputs_(num_inputs) {}

    size_t add_input(size_t var_idx) {
        if (var_idx >= num_inputs_) {
            throw std::out_of_range("Індекс змінної виходить за межі num_inputs");
        }
        size_t id = gates_.size();
        gates_.push_back(Gate{id, GateType::Input, var_idx, {}, 0});
        return id;
    }

    size_t add_gate(GateType type, std::vector<size_t> inputs) {
        size_t id = gates_.size();
        gates_.push_back(Gate{id, type, 0, std::move(inputs), 0});
        return id;
    }

    void set_output(size_t gate_id) {
        if (gate_id >= gates_.size()) {
            throw std::out_of_range("Невірний ID вихідного гейта");
        }
        output_id_ = gate_id;
    }

    uint8_t evaluate(std::span<const uint8_t> input_vector) const {
        if (input_vector.size() < num_inputs_) {
            throw std::invalid_argument("Недостатня довжина вхідного вектора бітів");
        }

        for (const auto& g : gates_) {
            switch (g.type) {
                case GateType::Input:
                    g.cached_value = input_vector[g.input_var_idx];
                    break;
                case GateType::Not:
                    g.cached_value = !gates_.at(g.fan_in.at(0)).cached_value;
                    break;
                case GateType::And: {
                    uint8_t res = 1;
                    for (size_t in_id : g.fan_in) {
                        if (!gates_.at(in_id).cached_value) {
                            res = 0;
                            break; /* Насичення AND */
                        }
                    }
                    g.cached_value = res;
                    break;
                }
                case GateType::Or: {
                    uint8_t res = 0;
                    for (size_t in_id : g.fan_in) {
                        if (gates_.at(in_id).cached_value) {
                            res = 1;
                            break; /* Насичення OR */
                        }
                    }
                    g.cached_value = res;
                    break;
                }
            }
        }
        return gates_.at(output_id_).cached_value;
    }

    std::vector<VariableState> sample_random_restriction(double p) const {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::bernoulli_distribution free_dist(p);
        std::bernoulli_distribution bit_dist(0.5);

        std::vector<VariableState> restriction(num_inputs_);
        for (size_t i = 0; i < num_inputs_; ++i) {
            if (free_dist(gen)) {
                restriction[i] = VariableState::Free;
            } else {
                restriction[i] = bit_dist(gen) ? VariableState::One : VariableState::Zero;
            }
        }
        return restriction;
    }

    [[nodiscard]] size_t gate_count() const noexcept { return gates_.size(); }

private:
    size_t num_inputs_;
    std::vector<Gate> gates_;
    size_t output_id_{0};
};

int main() {
    try {
        AC0Circuit circuit(8);
        std::vector<size_t> in_ids(8);
        for (size_t i = 0; i < 8; ++i) in_ids[i] = circuit.add_input(i);

        // Побудова ДНФ другого рівня з 4 кон'юнкцій
        std::vector<size_t> and_gates;
        for (size_t i = 0; i < 8; i += 2) {
            and_gates.push_back(circuit.add_gate(GateType::And, {in_ids[i], in_ids[i+1]}));
        }
        size_t top_or = circuit.add_gate(GateType::Or, and_gates);
        circuit.set_output(top_or);

        std::vector<uint8_t> input_data = {1, 1, 0, 1, 0, 0, 1, 0};
        uint8_t out_val = circuit.evaluate(input_data);
        std::cout << "Результат обчислення AC0 ДНФ на C++: " 
                  << static_cast<int>(out_val) << "\n";

        auto restriction = circuit.sample_random_restriction(0.25);
        std::cout << "Згенероване обмеження rho (p = 0.25): ";
        for (auto st : restriction) {
            if (st == VariableState::Free) std::cout << "* ";
            else std::cout << static_cast<int>(st) << " ";
        }
        std::cout << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка симуляції: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
