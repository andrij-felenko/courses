#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <string_view>
#include <chrono>

namespace link_fallback {

enum class BearerId : uint8_t {
    PrimaryHighSpeed = 0,
    FallbackSubGhz   = 1,
    Count            = 2
};

enum class ArbiterState : uint8_t {
    PrimaryActive,
    FallbackActive,
    RecoveryEvaluation,
    EmergencyBlackout
};

enum class PacketPriority : uint8_t {
    CriticalCommand = 0,
    Telemetry       = 1,
    BulkVideo       = 2
};

enum class TransmitError {
    LinkBlackout,
    PayloadTooLarge,
    DroppedLowPriority,
    HardwareFault
};

struct LinkQualityMetrics {
    int16_t  rssiDbm{-60};
    int8_t   snrDb{20};
    uint8_t  packetErrorRate{0};
    uint8_t  compositeScore{100};
    uint32_t packetWindowMask{0xFFFFFFFF};
    std::chrono::milliseconds lastRxTime{0};

    void recordPacket(int16_t rawRssi, int8_t rawSnr, std::chrono::milliseconds now) noexcept {
        lastRxTime = now;
        rssiDbm = static_cast<int16_t>((rssiDbm * 7 + rawRssi) >> 3);
        snrDb = static_cast<int8_t>((snrDb * 7 + rawSnr) >> 3);
        packetWindowMask = (packetWindowMask << 1) | 1U;
        computeStats();
    }

    void recordLoss() noexcept {
        packetWindowMask = (packetWindowMask << 1);
        computeStats();
    }

private:
    void computeStats() noexcept {
        uint32_t count = 0;
        uint32_t temp = packetWindowMask;
        while (temp) {
            count += (temp & 1U);
            temp >>= 1;
        }
        packetErrorRate = static_cast<uint8_t>(((32 - count) * 100) / 32);
        int score = 100 - packetErrorRate;
        if (rssiDbm < -100) score -= 20;
        compositeScore = static_cast<uint8_t>(score < 0 ? 0 : (score > 100 ? 100 : score));
    }
};

class MultiLinkArbiter {
public:
    static constexpr std::chrono::milliseconds kHysteresisDwell{5000};
    static constexpr uint8_t kFailoverPerThresh{25};
    static constexpr uint8_t kRecoveryPerThresh{5};

    MultiLinkArbiter() noexcept
        : currentState_(ArbiterState::PrimaryActive),
          activeBearer_(BearerId::PrimaryHighSpeed),
          stateEnterTime_(std::chrono::milliseconds{0}) {}

    [[nodiscard]] ArbiterState state() const noexcept { return currentState_; }
    [[nodiscard]] BearerId activeBearer() const noexcept { return activeBearer_; }
    [[nodiscard]] const LinkQualityMetrics& metrics(BearerId id) const noexcept {
        return metrics_[static_cast<size_t>(id)];
    }

    void onPacketReceived(BearerId id, int16_t rssi, int8_t snr, std::chrono::milliseconds now) noexcept {
        metrics_[static_cast<size_t>(id)].recordPacket(rssi, snr, now);
    }

    void update(std::chrono::milliseconds now) noexcept {
        const auto& prim = metrics_[static_cast<size_t>(BearerId::PrimaryHighSpeed)];
        const auto& fall = metrics_[static_cast<size_t>(BearerId::FallbackSubGhz)];

        const bool primFailed = (now - prim.lastRxTime > std::chrono::milliseconds{1500}) ||
                                (prim.packetErrorRate >= kFailoverPerThresh);
        const bool fallFailed = (now - fall.lastRxTime > std::chrono::milliseconds{3000});

        switch (currentState_) {
        case ArbiterState::PrimaryActive:
            if (primFailed) {
                currentState_ = ArbiterState::FallbackActive;
                activeBearer_ = BearerId::FallbackSubGhz;
                stateEnterTime_ = now;
            }
            break;

        case ArbiterState::FallbackActive:
            if (primFailed && fallFailed) {
                currentState_ = ArbiterState::EmergencyBlackout;
                stateEnterTime_ = now;
            } else if (!primFailed && prim.packetErrorRate <= kRecoveryPerThresh) {
                currentState_ = ArbiterState::RecoveryEvaluation;
                stateEnterTime_ = now;
            }
            break;

        case ArbiterState::RecoveryEvaluation:
            if (primFailed) {
                currentState_ = ArbiterState::FallbackActive;
                activeBearer_ = BearerId::FallbackSubGhz;
            } else if (now - stateEnterTime_ >= kHysteresisDwell) {
                currentState_ = ArbiterState::PrimaryActive;
                activeBearer_ = BearerId::PrimaryHighSpeed;
            }
            break;

        case ArbiterState::EmergencyBlackout:
            if (!fallFailed) {
                currentState_ = ArbiterState::FallbackActive;
                activeBearer_ = BearerId::FallbackSubGhz;
            } else if (!primFailed) {
                currentState_ = ArbiterState::PrimaryActive;
                activeBearer_ = BearerId::PrimaryHighSpeed;
            }
            break;
        }
    }

    [[nodiscard]] std::expected<size_t, TransmitError> routePacket(
        PacketPriority priority,
        std::span<const uint8_t> payload
    ) noexcept {
        if (currentState_ == ArbiterState::EmergencyBlackout) {
            return std::unexpected(TransmitError::LinkBlackout);
        }

        if (priority == PacketPriority::BulkVideo && activeBearer_ == BearerId::FallbackSubGhz) {
            return std::unexpected(TransmitError::DroppedLowPriority);
        }

        if (payload.size() > 256) {
            return std::unexpected(TransmitError::PayloadTooLarge);
        }

        /* Імітація успішної відправки через драйвер активного інтерфейсу */
        return payload.size();
    }

private:
    ArbiterState currentState_;
    BearerId activeBearer_;
    std::chrono::milliseconds stateEnterTime_;
    std::array<LinkQualityMetrics, static_cast<size_t>(BearerId::Count)> metrics_{};
};

} // namespace link_fallback
