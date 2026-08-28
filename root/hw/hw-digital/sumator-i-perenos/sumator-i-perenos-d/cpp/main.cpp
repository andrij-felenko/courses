#include <iostream>
#include <iomanip>
#include <cstdint>
#include <array>
#include <span>
#include <concepts>

// Результат моделювання суматора з метриками затримки
struct AdderEvaluation {
    std::uint64_t sum{0};
    std::uint8_t  carry_out{0};
    std::uint32_t logic_depth{0};
};

// Абстрактний інтерфейс цифрового суматора
class DigitalAdder64 {
public:
    virtual ~DigitalAdder64() = default;
    [[nodiscard]] virtual AdderEvaluation add(std::uint64_t a, std::uint64_t b, std::uint8_t cin) const = 0;
};

// 64-розрядний ланцюговий суматор (Ripple Carry Adder)
class RippleCarryAdder64 final : public DigitalAdder64 {
public:
    [[nodiscard]] AdderEvaluation add(std::uint64_t a, std::uint64_t b, std::uint8_t cin) const override {
        AdderEvaluation eval;
        std::uint8_t carry = cin & 1U;

        for (std::size_t i = 0; i < 64; ++i) {
            const auto ai = static_cast<std::uint8_t>((a >> i) & 1U);
            const auto bi = static_cast<std::uint8_t>((b >> i) & 1U);

            const auto prop = static_cast<std::uint8_t>(ai ^ bi);
            const auto gen  = static_cast<std::uint8_t>(ai & bi);
            const auto sum_bit = static_cast<std::uint8_t>(prop ^ carry);

            carry = static_cast<std::uint8_t>(gen | (carry & prop));
            eval.sum |= (static_cast<std::uint64_t>(sum_bit) << i);
        }

        eval.carry_out = carry;
        // 1 рівень генерації P + 64 комірки * 2 рівні вентилів на перенос + 1 рівень XOR суми
        eval.logic_depth = 1 + (64 * 2) + 1;
        return eval;
    }
};

// 64-розрядний паралельний префіксний суматор Коггі-Стоуна (Kogge-Stone Adder)
class KoggeStoneAdder64 final : public DigitalAdder64 {
public:
    [[nodiscard]] AdderEvaluation add(std::uint64_t a, std::uint64_t b, std::uint8_t cin) const override {
        AdderEvaluation eval;
        std::array<std::uint8_t, 64> gen{};
        std::array<std::uint8_t, 64> prop{};

        // Етап 1: Попередня генерація бітових сигналів G та P
        for (std::size_t i = 0; i < 64; ++i) {
            const auto ai = static_cast<std::uint8_t>((a >> i) & 1U);
            const auto bi = static_cast<std::uint8_t>((b >> i) & 1U);
            gen[i]  = static_cast<std::uint8_t>(ai & bi);
            prop[i] = static_cast<std::uint8_t>(ai ^ bi);
        }

        gen[0] = static_cast<std::uint8_t>(gen[0] | (prop[0] & (cin & 1U)));

        auto cur_g = gen;
        auto cur_p = prop;
        std::uint32_t prefix_layers = 0;

        // Етап 2: Паралельне префіксне дерево (log2(64) = 6 ярусів)
        for (std::size_t stride = 1; stride < 64; stride <<= 1U) {
            auto next_g = cur_g;
            auto next_p = cur_p;

            for (std::size_t i = stride; i < 64; ++i) {
                // Асоціативний оператор префіксної композиції: (G_L | (P_L & G_R), P_L & P_R)
                next_g[i] = static_cast<std::uint8_t>(cur_g[i] | (cur_p[i] & cur_g[i - stride]));
                next_p[i] = static_cast<std::uint8_t>(cur_p[i] & cur_p[i - stride]);
            }

            cur_g = next_g;
            cur_p = next_p;
            ++prefix_layers;
        }

        // Етап 3: Фінальне обчислення бітів суми S_i = P_i ^ C_{i-1}
        for (std::size_t i = 0; i < 64; ++i) {
            const std::uint8_t carry_in_bit = (i == 0) ? (cin & 1U) : cur_g[i - 1];
            const auto sum_bit = static_cast<std::uint8_t>(prop[i] ^ carry_in_bit);
            eval.sum |= (static_cast<std::uint64_t>(sum_bit) << i);
        }

        eval.carry_out = cur_g[63];
        // 1 рівень генерації P/G + 6 ярусів префіксів * 2 вентилі (AND-OR) + 1 рівень XOR
        eval.logic_depth = 1 + (prefix_layers * 2) + 1;
        return eval;
    }
};

int main() {
    constexpr std::uint64_t op_a = 0x7FFFFFFFFFFFFFFFULL;
    constexpr std::uint64_t op_b = 0x0000000000000001ULL;
    constexpr std::uint8_t  cin  = 0;

    const RippleCarryAdder64 rca;
    const KoggeStoneAdder64  ksa;

    const auto res_rca = rca.add(op_a, op_b, cin);
    const auto res_ksa = ksa.add(op_a, op_b, cin);
    const auto expected = op_a + op_b + cin;

    std::cout << "64-Bit Adder Benchmark & Gate Depth Analysis\n"
              << "Operand A:        0x" << std::hex << std::setw(16) << std::setfill('0') << op_a << "\n"
              << "Operand B:        0x" << std::hex << std::setw(16) << std::setfill('0') << op_b << "\n"
              << "Expected Sum:     0x" << std::hex << std::setw(16) << std::setfill('0') << expected << "\n\n"
              << std::dec
              << "Ripple Carry:     0x" << std::hex << std::setw(16) << std::setfill('0') << res_rca.sum
              << std::dec << " | Critical Path: " << res_rca.logic_depth << " gate levels\n"
              << "Kogge-Stone:      0x" << std::hex << std::setw(16) << std::setfill('0') << res_ksa.sum
              << std::dec << " | Critical Path: " << res_ksa.logic_depth << " gate levels\n\n";

    if (res_rca.sum == expected && res_ksa.sum == expected) {
        const double speedup = static_cast<double>(res_rca.logic_depth) / static_cast<double>(res_ksa.logic_depth);
        std::cout << "Verification: SUCCESSFUL.\n"
                  << "Critical path reduction factor: " << std::fixed << std::setprecision(2) << speedup << "x\n";
    }

    return 0;
}
