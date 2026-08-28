// cpp — Ідіоматичний симулятор схем AC0 на C++20
#include <iostream>
#include <vector>
#include <memory>
#include <numeric>
#include <random>
#include <stdexcept>
#include <span >

enum class GateType { Input, Not, And, Or };

struct Gate {
    size_t id;
    GateType type;
    size_t input_var_idx{0};
    std::vector<size_t> fan_in;
    mutable uint8_t cached_value{0};
};

class AC0Circuit {
public:
    explicit AC0Circuit(size_t num_inputs) : num_inputs_(num_inputs) {}

    size_t add_input(size_t var_idx) {
        if (var_idx >= num_inputs_) throw std::out_of_range("Індекс змінної виходить за межі");
        size_t id = gates_.size();
        gates_.push_back(Gate{id, GateType::Input, var_idx, {}, 0});
        return id;
    }

    size_t add_gate(GateType type, std::vector<size_t> inputs) {
        size_t id = gates_.size();
        gates_.push_back(Gate{id, type, 0, std::move(inputs), 0});
        return id;
    }

    void set_output(size_t gate_id) { output_id_ = gate_id; }

    uint8_t evaluate(std::span<const uint8_t> input_vector) const {
        if (input_vector.size() < num_inputs_) {
            throw std::invalid_argument("Недостатня довжина вхідного вектора");
        }
        for (const auto& g : gates_) {
            switch (g.type) {
                case GateType::Input:
                    g.cached_value = input_vector[g.input_var_idx];
                    break;
                case GateType::Not:
                    g.cached_value = !gates_[g.fan_in.at(0)].cached_value;
                    break;
                case GateType::And: {
                    uint8_t res = 1;
                    for (size_t in_id : g.fan_in) {
                        if (!gates_[in_id].cached_value) { res = 0; break; }
                    }
                    g.cached_value = res;
                    break;
                }
                case GateType::Or: {
                    uint8_t res = 0;
                    for (size_t in_id : g.fan_in) {
                        if (gates_[in_id].cached_value) { res = 1; break; }
                    }
                    g.cached_value = res;
                    break;
                }
            }
        }
        return gates_.at(output_id_).cached_value;
    }

private:
    size_t num_inputs_;
    std::vector<Gate> gates_;
    size_t output_id_{0};
};

int main() {
    AC0Circuit circuit(4);
    std::vector<size_t> inputs;
    for (size_t i = 0; i < 4; ++i) inputs.push_back(circuit.add_input(i));

    size_t and_gate = circuit.add_gate(GateType::And, {inputs[0], inputs[1]});
    size_t out_gate = circuit.add_gate(GateType::Or, {and_gate, inputs[2]});
    circuit.set_output(out_gate);

    std::vector<uint8_t> input_bits = {1, 1, 0, 0};
    std::cout << "Результат обчислення C++ AC0 схеми: " 
              << static_cast<int>(circuit.evaluate(input_bits)) << "\n";
    return 0;
}
