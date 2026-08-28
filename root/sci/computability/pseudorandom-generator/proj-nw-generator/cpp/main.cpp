#include <iostream>
#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>
#include <stdexcept>

class NisanWigdersonPRG {
public:
    static constexpr std::size_t kSeedLen = 16;
    static constexpr std::size_t kSubsetLen = 6;
    static constexpr std::size_t kOutLen = 32;

    NisanWigdersonPRG() {
        buildCombinatorialDesign();
    }

    // Обчислення бітового потоку за вхідним насінням
    [[nodiscard]] std::vector<uint8_t> generate(std::span<const uint8_t> seed) const {
        if (seed.size() * 8 < kSeedLen) {
            throw std::invalid_argument("Довжина насіння занадто мала");
        }

        std::vector<uint8_t> out_bits(kOutLen, 0);
        for (std::size_t i = 0; i < kOutLen; ++i) {
            out_bits[i] = generateBit(seed, i);
        }
        return out_bits;
    }

private:
    std::vector<std::vector<std::size_t>> design_matrix_;

    void buildCombinatorialDesign() {
        design_matrix_.resize(kOutLen, std::vector<std::size_t>(kSubsetLen));
        for (std::size_t i = 0; i < kOutLen; ++i) {
            for (std::size_t j = 0; j < kSubsetLen; ++j) {
                design_matrix_[i][j] = (i * 3 + j * 2 + (i * j)) % kSeedLen;
            }
        }
    }

    [[nodiscard]] static uint8_t hardCoreFunction(uint32_t bits) noexcept {
        uint8_t parity = 0;
        uint32_t temp = bits;
        while (temp > 0) {
            parity ^= (temp & 1);
            temp >>= 1;
        }
        uint8_t b0 = (bits >> 0) & 1;
        uint8_t b1 = (bits >> 1) & 1;
        uint8_t b2 = (bits >> 2) & 1;
        return parity ^ (b0 & b1) ^ (b1 & b2);
    }

    [[nodiscard]] uint8_t generateBit(std::span<const uint8_t> seed, std::size_t idx) const noexcept {
        uint32_t sub_val = 0;
        for (std::size_t j = 0; j < kSubsetLen; ++j) {
            std::size_t pos = design_matrix_[idx][j];
            uint8_t bit = (seed[pos / 8] >> (pos % 8)) & 1;
            sub_val |= (static_cast<uint32_t>(bit) << j);
        }
        return hardCoreFunction(sub_val);
    }
};

int main() {
    try {
        NisanWigdersonPRG generator;
        const std::vector<uint8_t> seed = { 0xA5, 0x5C };

        const auto pseudorandom_bits = generator.generate(seed);

        std::cout << "Псевдовипадковий бітовий потік NW PRG (C++20, m = " 
                  << NisanWigdersonPRG::kOutLen << " біт):\n";
        for (std::size_t i = 0; i < pseudorandom_bits.size(); ++i) {
            std::cout << static_cast<int>(pseudorandom_bits[i]);
            if ((i + 1) % 8 == 0) std::cout << ' ';
        }
        std::cout << '\n';
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
