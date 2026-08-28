#pragma once

#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <algorithm>
#include <span>
#include <concepts>

namespace realtime::control {

using Microseconds = std::chrono::microseconds;

template <typename T, size_t Dim>
struct PredictionFrame {
    std::array<T, Dim> values{};
    Microseconds timestamp{0};
    uint32_t frameId{0};
    T confidence{1.0f};
};

enum class ControlStatus : uint8_t {
    Fresh = 0,
    Extrapolated,
    FallbackPid,
    EmergencyStop
};

struct WatchdogConfig {
    Microseconds deadlineLimit{40'000};
    Microseconds maxExtrapolation{90'000};
    Microseconds fatalTimeout{400'000};
    float decayLambda{12.0f};
    float maxSlewRate{50.0f};
};

template <typename T, size_t Dim>
class LockFreeTripleBuffer {
public:
    using Frame = PredictionFrame<T, Dim>;

    LockFreeTripleBuffer() noexcept 
        : cleanIdx_{0}, writeIdx_{1}, readIdx_{2} {
        slots_.fill(Frame{});
    }

    void write(const Frame& frame) noexcept {
        slots_[writeIdx_] = frame;
        uint_fast8_t oldClean = cleanIdx_.exchange(writeIdx_, std::memory_order_release);
        writeIdx_ = static_cast<uint8_t>(oldClean);
    }

    [[nodiscard]] std::pair<Frame, bool> read() noexcept {
        uint_fast8_t currentClean = cleanIdx_.load(std::memory_order_acquire);
        bool fresh = false;

        if (currentClean != readIdx_) {
            uint_fast8_t oldClean = cleanIdx_.exchange(readIdx_, std::memory_order_acq_rel);
            readIdx_ = static_cast<uint8_t>(oldClean);
            fresh = true;
        }

        return { slots_[readIdx_], fresh };
    }

private:
    alignas(64) std::array<Frame, 3> slots_;
    alignas(64) std::atomic<uint_fast8_t> cleanIdx_;
    uint8_t writeIdx_;
    uint8_t readIdx_;
};

} // namespace realtime::control
