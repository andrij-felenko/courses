#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

namespace fleet {

class CohortClassifier {
public:
    static constexpr size_t kIdLen = 16;
    static constexpr size_t kSaltLen = 16;

    static uint8_t calculate_bucket(std::span<const uint8_t, kIdLen> hw_id,
                                    std::span<const uint8_t, kSaltLen> salt) noexcept {
        std::array<uint8_t, kIdLen + kSaltLen> buffer{};
        std::copy(hw_id.begin(), hw_id.end(), buffer.begin());
        std::copy(salt.begin(), salt.end(), buffer.begin() + kIdLen);

        uint32_t hash = 2166136261u;
        for (uint8_t byte : buffer) {
            hash ^= byte;
            hash *= 16777619u;
        }
        return static_cast<uint8_t>(hash % 100u);
    }

    static constexpr bool is_eligible(uint8_t cohort, uint8_t cutoff_percent) noexcept {
        return cohort < cutoff_percent;
    }
};

} // namespace fleet
