#include <iostream>
#include <vector>
#include <memory>
#include <cstdint>
#include <stdexcept>
#include <span>

namespace p_poly {

enum class GateType {
    InputX,
    AdviceA,
    Not,
    And,
    Or
};

struct Gate {
    GateType type;
    std::size_t param_idx{0};
    std::size_t in1{0};
    std::size_t in2{0};
};

class Circuit {
public:
    Circuit(std::size_t num_inputs, std::size_t num_advice, std::vector<Gate> gates)
        : num_inputs_(num_inputs), num_advice_(num_advice), gates_(std::move(gates)) {
        if (gates_.empty()) {
            throw std::invalid_argument("Circuit must contain at least one gate.");
        }
    }

    [[nodiscard]] bool evaluate(std::span<const std::uint8_t> x, std::span<const std::uint8_t> a_n) const {
        if (x.size() < num_inputs_) {
            throw std::invalid_argument("Input vector x is too short.");
        }
        if (a_n.size() < num_advice_) {
            throw std::invalid_argument("Advice vector a_n is too short.");
        }

        std::vector<bool> values(gates_.size(), false);

        for (std::size_t i = 0; i < gates_.size(); ++i) {
            const auto& g = gates_[i];
            switch (g.type) {
                case GateType::InputX:
                    values[i] = (x[g.param_idx] != 0);
                    break;
                case GateType::AdviceA:
                    values[i] = (a_n[g.param_idx] != 0);
                    break;
                case GateType::Not:
                    values[i] = !values.at(g.in1);
                    break;
                case GateType::And:
                    values[i] = values.at(g.in1) && values.at(g.in2);
                    break;
                case GateType::Or:
                    values[i] = values.at(g.in1) || values.at(g.in2);
                    break;
            }
        }

        return values.back();
    }

    [[nodiscard]] std::size_t gate_count() const noexcept { return gates_.size(); }

private:
    std::size_t num_inputs_;
    std::size_t num_advice_;
    std::vector<Gate> gates_;
};

} // namespace p_poly

int main() {
    using namespace p_poly;

    try {
        std::vector<Gate> gates = {
            { GateType::InputX, 0, 0, 0 },  // 0: x1
            { GateType::InputX, 1, 0, 0 },  // 1: x2
            { GateType::AdviceA, 0, 0, 0 }, // 2: a1
            { GateType::Not, 0, 2, 0 },     // 3: NOT a1
            { GateType::And, 0, 0, 1 },     // 4: x1 AND x2
            { GateType::Or, 0, 4, 3 }       // 5: (x1 AND x2) OR (NOT a1)
        };

        Circuit circuit(2, 1, std::move(gates));

        const std::vector<std::uint8_t> x = {1, 0};
        const std::vector<std::uint8_t> a_n = {0};

        bool result = circuit.evaluate(x, a_n);
        std::cout << "Результат обчислення C++: " << (result ? "TRUE (1)" : "FALSE (0)") << '\n';
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
