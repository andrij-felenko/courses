// cpp — Заголовочний файл C++20 класу AC0CircuitAPI
#ifndef AC0_CIRCUIT_API_HPP
#define AC0_CIRCUIT_API_HPP

#include <vector>
#include <memory>
#include <span >
#include <optional>
#include <string>
#include <cstddef>

namespace ac0 {

enum class GateKind { Input, Not, And, Or };

struct GateStats {
    size_t max_fan_in{0};
    size_t min_fan_in{0};
    double avg_fan_in{0.0};
    size_t max_fan_out{0};
};

class CircuitAPI {
public:
    virtual ~CircuitAPI() = default;

    virtual size_t add_input(size_t var_index) = 0;
    virtual size_t add_gate(GateKind kind, std::span<const size_t> inputs) = 0;
    virtual void set_output_gate(size_t gate_id) = 0;

    [[nodiscard]] virtual size_t get_depth() const = 0;
    [[nodiscard]] virtual size_t get_size() const = 0;
    [[nodiscard]] virtual GateStats get_stats() const = 0;
    [[nodiscard]] virtual bool is_valid_ac0(size_t max_depth, size_t max_size) const noexcept = 0;

    [[nodiscard]] virtual uint8_t evaluate(std::span<const uint8_t> input_bits) const = 0;
};

class CircuitBuilder : public CircuitAPI {
public:
    explicit CircuitBuilder(size_t num_inputs);
    ~CircuitBuilder() override = default;

    size_t add_input(size_t var_index) override;
    size_t add_gate(GateKind kind, std::span<const size_t> inputs) override;
    void set_output_gate(size_t gate_id) override;

    [[nodiscard]] size_t get_depth() const override;
    [[nodiscard]] size_t get_size() const override;
    [[nodiscard]] GateStats get_stats() const override;
    [[nodiscard]] bool is_valid_ac0(size_t max_depth, size_t max_size) const noexcept override;

    [[nodiscard]] uint8_t evaluate(std::span<const uint8_t> input_bits) const override;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace ac0

#endif // AC0_CIRCUIT_API_HPP
