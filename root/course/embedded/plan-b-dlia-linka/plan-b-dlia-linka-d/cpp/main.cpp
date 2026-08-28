#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <chrono>
#include <expected>

namespace embedded_link {

enum class Priority : uint8_t {
    CriticalCommand = 0,
    Telemetry       = 1,
    BulkStream      = 2
};

enum class RouteError {
    LinkBlackout,
    ThrottledOnFallback,
    BufferFull
};

struct ChannelMetrics {
    int16_t rssiDbm{-60};
    uint32_t rxMask{0xFFFFFFFF};
    uint8_t packetLossPercent{0};
    std::chrono::milliseconds lastRxMono{0};

    void update(int16_t rawRssi, std::chrono::milliseconds now) noexcept {
        lastRxMono = now;
        rssiDbm = static_cast<int16_t>((rssiDbm * 3 + rawRssi) >> 2);
        rxMask = (rxMask << 1) | 1U;
        recalcPer();
    }

    void recordLoss() noexcept {
        rxMask = (rxMask << 1);
        recalcPer();
    }

private:
    void recalcPer() noexcept {
        uint32_t temp = rxMask;
        uint32_t received = 0;
        for (size_t i = 0; i < 32; ++i) {
            if (temp & 1U) received++;
            temp >>= 1;
        }
        packetLossPercent = static_cast<uint8_t>(((32 - received) * 100) / 32);
    }
};

class LinkArbiter {
public:
    static constexpr std::chrono::milliseconds kDwellTime{4000};
    static constexpr uint8_t kFailoverPer{25};
    static constexpr uint8_t kRecoveryPer{5};

    void onPacketRx(size_t channelIdx, int16_t rssi, std::chrono::milliseconds now) noexcept {
        if (channelIdx < channels_.size()) {
            channels_[channelIdx].update(rssi, now);
        }
    }

    void poll(std::chrono::milliseconds now) noexcept {
        const auto& prim = channels_[0];
        const bool primFailed = (now - prim.lastRxMono > std::chrono::milliseconds{1200}) ||
                                (prim.packetLossPercent >= kFailoverPer);

        if (activeChannel_ == 0 && primFailed) {
            activeChannel_ = 1;
            hysteresisTimerStart_.reset();
        } else if (activeChannel_ == 1 && !primFailed && prim.packetLossPercent <= kRecoveryPer) {
            if (!hysteresisTimerStart_) {
                hysteresisTimerStart_ = now;
            } else if (now - *hysteresisTimerStart_ >= kDwellTime) {
                activeChannel_ = 0;
                hysteresisTimerStart_.reset();
            }
        } else {
            hysteresisTimerStart_.reset();
        }
    }

    [[nodiscard]] std::expected<size_t, RouteError> dispatch(
        Priority prio,
        std::span<const uint8_t> payload
    ) const noexcept {
        if (prio == Priority::BulkStream && activeChannel_ == 1) {
            return std::unexpected(RouteError::ThrottledOnFallback);
        }
        return payload.size();
    }

    [[nodiscard]] size_t activeIndex() const noexcept { return activeChannel_; }

private:
    size_t activeChannel_{0};
    std::optional<std::chrono::milliseconds> hysteresisTimerStart_{std::nullopt};
    std::array<ChannelMetrics, 2> channels_{};
};

} // namespace embedded_link
