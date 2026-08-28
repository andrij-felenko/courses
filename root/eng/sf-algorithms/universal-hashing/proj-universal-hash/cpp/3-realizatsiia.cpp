#include <cstdint>
#include <cstddef>
#include <array>
#include <random>
#include <span>

namespace universal_hashing {

class TabulationHasher {
public:
    TabulationHasher(uint32_t M, std::mt19937_64& rng) : mask_{(1ULL << M) - 1} {
        for (auto& row : table_) {
            for (auto& cell : row) {
                cell = rng();
            }
        }
    }

    [[nodiscard]] uint64_t operator()(uint64_t x) const noexcept {
        uint64_t hash = 0;
        const auto* bytes = reinterpret_cast<const uint8_t*>(&x);
        for (size_t i = 0; i < 8; ++i) {
            hash ^= table_[i][bytes[i]];
        }
        return hash & mask_;
    }

private:
    std::array<std::array<uint64_t, 256>, 8> table_{};
    uint64_t mask_;
};

} // namespace universal_hashing
