#include <cstdint>
#include <chrono>
#include <string_view>

namespace truetime {

using Nanoseconds = std::chrono::nanoseconds;
using Microseconds = std::chrono::microseconds;

/* Часовий інтервал TrueTime на базі стандартних типів chrono */
struct Interval {
    Nanoseconds earliest{0};
    Nanoseconds latest{0};

    [[nodiscard]] constexpr Nanoseconds width() const noexcept {
        return latest - earliest;
    }

    [[nodiscard]] constexpr Nanoseconds uncertainty() const noexcept {
        return width() / 2;
    }

    [[nodiscard]] constexpr bool contains(Nanoseconds t) const noexcept {
        return earliest <= t && t <= latest;
    }
};

enum class SourceStatus : std::uint8_t {
    GpsLocked = 0,
    PtpLocked = 1,
    AtomicHoldover = 2,
    NtpFallback = 3,
    Unsynchronized = 4
};

struct Diagnostics {
    SourceStatus status{SourceStatus::Unsynchronized};
    Nanoseconds current_uncertainty{0};
    Nanoseconds max_allowed_uncertainty{0};
    Nanoseconds time_since_last_sync{0};
    std::int32_t active_satellites{0};
    double estimated_drift_ppm{0.0};
};

} // namespace truetime
