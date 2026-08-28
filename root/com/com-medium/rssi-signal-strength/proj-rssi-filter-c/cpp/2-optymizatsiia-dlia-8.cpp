#include <cstdint>
#include <optional>

class RssiFilterFixed {
public:
    constexpr explicit RssiFilterFixed(float alpha) noexcept
        : alphaQ16_(static_cast<int32_t>(alpha * 65536.0f)) {}

    [[nodiscard]] constexpr int32_t update(int32_t rawRssiDbm) noexcept {
        const int32_t rawQ16 = rawRssiDbm << 16;

        if (!filteredRssiQ16_) {
            filteredRssiQ16_ = rawQ16;
        } else {
            const int64_t term1 = static_cast<int64_t>(alphaQ16_) * rawQ16;
            const int64_t term2 = static_cast<int64_t>(65536 - alphaQ16_) * (*filteredRssiQ16_);
            filteredRssiQ16_ = static_cast<int32_t>((term1 + term2) >> 16);
        }

        return *filteredRssiQ16_ >> 16;
    }

private:
    int32_t alphaQ16_{9830}; // За замовчуванням 0.15 * 65536
    std::optional<int32_t> filteredRssiQ16_{std::nullopt};
};
