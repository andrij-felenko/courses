#include <cstdint>
#include <concepts>
#include <limits>
#include <optional>
#include <type_traits>

// ── 1. Конвертер форматів часових міток ──────────────────────────────────────

class TimestampConverter {
public:
    static constexpr uint64_t NTP_TO_UNIX_EPOCH_OFFSET = 2208988800ULL;

    [[nodiscard]] static constexpr uint32_t nsec_to_ntp_fraction(uint32_t nsec) noexcept {
        if (nsec >= 1'000'000'000U) {
            nsec = 999'999'999U;
        }
        uint64_t scaled = (static_cast<uint64_t>(nsec) << 32) + 500'000'000ULL;
        return static_cast<uint32_t>(scaled / 1'000'000'000ULL);
    }

    [[nodiscard]] static constexpr uint32_t ntp_fraction_to_nsec(uint32_t ntp_frac) noexcept {
        uint64_t prod = static_cast<uint64_t>(ntp_frac) * 1'000'000'000ULL + 0x8000'0000ULL;
        return static_cast<uint32_t>(prod >> 32);
    }

    [[nodiscard]] static constexpr int64_t scale_to_sub_nanoseconds(int64_t nsec, uint16_t sub_ns_frac = 0) noexcept {
        return (nsec << 16) | (sub_ns_frac & 0xFFFF);
    }

    [[nodiscard]] static constexpr int64_t sub_nanoseconds_to_nsec(int64_t correction_field) noexcept {
        return correction_field >> 16;
    }
};

// ── 2. Узагальнений розгортач циклічних лічильників (Unwrapper) ───────────────

template <std::unsigned_integral RawType, std::signed_integral OutputType = int64_t>
class ModularTimestampUnwrapper {
    using SignedDiffType = std::make_signed_t<RawType>;

    std::optional<RawType> last_raw_{};
    OutputType accumulated_epoch_{0};

public:
    constexpr void reset() noexcept {
        last_raw_.reset();
        accumulated_epoch_ = 0;
    }

    [[nodiscard]] OutputType update(RawType raw_value) noexcept {
        if (!last_raw_.has_value()) {
            last_raw_ = raw_value;
            accumulated_epoch_ = static_cast<OutputType>(raw_value);
            return accumulated_epoch_;
        }

        // Обчислення знакової різниці в модульному просторі
        SignedDiffType delta = static_cast<SignedDiffType>(raw_value - *last_raw_);
        accumulated_epoch_ += static_cast<OutputType>(delta);
        last_raw_ = raw_value;

        return accumulated_epoch_;
    }

    [[nodiscard]] OutputType current_value() const noexcept {
        return accumulated_epoch_;
    }
};

// Спеціалізація для 32-бітного RTP та апаратних таймерів
using RtpTimestampUnwrapper = ModularTimestampUnwrapper<uint32_t, int64_t>;
