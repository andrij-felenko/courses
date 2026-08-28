// Ідіоматичний C++20 модуль обробки диференційного АЦП
#include <array>
#include <numeric>
#include <cstdint>
#include <expected>
#include <span>

enum class AdcError {
    Timeout,
    SaturationPositive,
    SaturationNegative,
    ReferenceFault
};

template <std::size_t WindowSize = 16>
class DifferentialAdcFilter {
public:
    static constexpr std::int64_t VrefMicrovolts = 3'300'000;
    static constexpr std::int32_t MaxCode24Bit = 8'388'607;

    constexpr DifferentialAdcFilter() = default;

    constexpr void reset() noexcept {
        samples_.fill(0);
        index_ = 0;
        count_ = 0;
        sum_ = 0;
    }

    constexpr std::int32_t push(std::int32_t raw_code) noexcept {
        if (count_ >= WindowSize) {
            sum_ -= samples_[index_];
        } else {
            ++count_;
        }

        samples_[index_] = raw_code;
        sum_ += raw_code;
        index_ = (index_ + 1) % WindowSize;

        return static_cast<std::int32_t>(sum_ / static_cast<std::int64_t>(count_));
    }

    [[nodiscard]] static constexpr std::expected<std::int32_t, AdcError>
    codeToMicrovolts(std::int32_t code) noexcept {
        if (code >= MaxCode24Bit) {
            return std::unexpected(AdcError::SaturationPositive);
        }
        if (code <= -MaxCode24Bit) {
            return std::unexpected(AdcError::SaturationNegative);
        }

        const auto uv = (static_cast<std::int64_t>(code) * VrefMicrovolts) / MaxCode24Bit;
        return static_cast<std::int32_t>(uv);
    }

    [[nodiscard]] constexpr std::span<const std::int32_t> rawHistory() const noexcept {
        return std::span<const std::int32_t>(samples_.data(), count_);
    }

private:
    std::array<std::int32_t, WindowSize> samples_{};
    std::size_t index_{0};
    std::size_t count_{0};
    std::int64_t sum_{0};
};
