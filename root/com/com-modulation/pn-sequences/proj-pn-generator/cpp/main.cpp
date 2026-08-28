#include <iostream>
#include <vector>
#include <cstdint>
#include <numeric>
#include <span>
#include <expected>
#include <string_view>

enum class LfsrTopology {
    Fibonacci,
    Galois
};

enum class LfsrError {
    InvalidState,
    ZeroSeedForbidden
};

class LfsrGenerator {
public:
    constexpr LfsrGenerator(uint32_t poly_mask, uint8_t bit_width, uint32_t seed, LfsrTopology topo)
        : mask_(poly_mask), bits_(bit_width), topology_(topo) {
        state_ = (seed == 0) ? 1U : (seed & ((1U << bits_) - 1U));
    }

    [[nodiscard]] uint8_t step() noexcept {
        if (topology_ == LfsrTopology::Galois) {
            uint8_t out_bit = state_ & 1U;
            state_ >>= 1U;
            if (out_bit != 0) {
                state_ ^= mask_;
            }
            return out_bit;
        } else {
            uint8_t out_bit = (state_ >> (bits_ - 1)) & 1U;
            uint32_t tapped = state_ & mask_;
            uint8_t feedback = 0;
            while (tapped > 0) {
                feedback ^= (tapped & 1U);
                tapped >>= 1U;
            }
            state_ = ((state_ << 1U) | feedback) & ((1U << bits_) - 1U);
            return out_bit;
        }
    }

    [[nodiscard]] uint32_t state() const noexcept { return state_; }

private:
    uint32_t state_{1};
    uint32_t mask_{0};
    uint8_t  bits_{5};
    LfsrTopology topology_{LfsrTopology::Galois};
};

class GoldCodeGenerator {
public:
    GoldCodeGenerator(uint32_t poly1, uint32_t poly2, uint8_t bits, uint32_t shift2)
        : gen1_(poly1, bits, 1, LfsrTopology::Galois),
          gen2_(poly2, bits, 1, LfsrTopology::Galois) {
        for (uint32_t i = 0; i < shift2; ++i) {
            gen2_.step();
        }
    }

    [[nodiscard]] std::vector<int8_t> generate_bipolar(size_t length) {
        std::vector<int8_t> buffer(length);
        for (size_t i = 0; i < length; ++i) {
            uint8_t b1 = gen1_.step();
            uint8_t b2 = gen2_.step();
            uint8_t gold_bit = b1 ^ b2;
            buffer[i] = (gold_bit == 0) ? int8_t{1} : int8_t{-1};
        }
        return buffer;
    }

private:
    LfsrGenerator gen1_;
    LfsrGenerator gen2_;
};

[[nodiscard]] int32_t compute_autocorrelation(std::span<const int8_t> sequence, size_t shift) noexcept {
    const size_t len = sequence.size();
    int32_t accum = 0;
    for (size_t i = 0; i < len; ++i) {
        size_t shifted_idx = (i + shift) % len;
        accum += static_cast<int32_t>(sequence[i]) * static_cast<int32_t>(sequence[shifted_idx]);
    }
    return accum;
}

int main() {
    constexpr uint8_t bits = 5;
    constexpr size_t N = (1U << bits) - 1U;

    GoldCodeGenerator gold_gen(0x12U, 0x1EU, bits, 3);
    const auto bipolar_seq = gold_gen.generate_bipolar(N);

    std::cout << "Період послідовності N = " << N << "\n";
    std::cout << "АКФ на зсуві 0: " << compute_autocorrelation(bipolar_seq, 0) << "\n";
    std::cout << "АКФ на зсуві 1: " << compute_autocorrelation(bipolar_seq, 1) << "\n";
    std::cout << "АКФ на зсуві 2: " << compute_autocorrelation(bipolar_seq, 2) << "\n";

    return 0;
}
