#include <cstdint>
#include <chrono>
#include <functional>
#include <bitset>
#include <algorithm>

enum class LinkState {
    Lost = 0,
    Degraded = 1,
    Connected = 2
};

class LinkWatchdog {
public:
    using Milliseconds = std::chrono::milliseconds;
    using TimePoint = std::chrono::steady_clock::time_point;

    struct Config {
        Milliseconds warningTimeout{1500};
        Milliseconds failsafeTimeout{3500};
        uint32_t recoveryHeartbeats{3};
        uint8_t lossThresholdPercent{40};
    };

    explicit LinkWatchdog(Config config = {})
        : config_(config), state_(LinkState::Lost) {}

    // Реєстрація зворотного виклику для оповіщення про зміну стану лінку
    void onStateChanged(std::function<void(LinkState oldState, LinkState newState)> callback) {
        stateCallback_ = std::move(callback);
    }

    // Реєстрація будь-якого отриманого MAVLink пакета для підрахунку втрат
    void feedPacket(uint8_t seq, TimePoint now = std::chrono::steady_clock::now()) {
        lastAnyPacketTime_ = now;
        if (!hasReceivedAny_) {
            hasReceivedAny_ = true;
            lastSequence_ = seq;
            packetWindow_.reset();
            packetWindow_.set(0, true);
            return;
        }

        uint8_t diff = static_cast<uint8_t>(seq - lastSequence_);
        if (diff > 0 && diff < 128) {
            if (diff >= packetWindow_.size()) {
                packetWindow_.reset();
            } else {
                packetWindow_ <<= diff;
            }
            packetWindow_.set(0, true);
            lastSequence_ = seq;
        }
    }

    // Оновлення розрахункової затримки RTT та варіації за алгоритмом EWMA
    void feedRtt(Milliseconds measuredRtt) noexcept {
        if (smoothedRtt_ == Milliseconds{0}) {
            smoothedRtt_ = measuredRtt;
            rttVariance_ = measuredRtt / 2;
        } else {
            auto delta = std::chrono::abs(measuredRtt - smoothedRtt_);
            rttVariance_ = (rttVariance_ * 3 + delta) / 4;
            smoothedRtt_ = (smoothedRtt_ * 7 + measuredRtt) / 8;
        }
    }

    // Реєстрація кадру пульсу HEARTBEAT
    void feedHeartbeat(uint8_t seq, TimePoint now = std::chrono::steady_clock::now()) {
        feedPacket(seq, now);
        lastHeartbeatTime_ = now;
        consecutiveHeartbeats_++;

        if (state_ == LinkState::Lost && consecutiveHeartbeats_ >= config_.recoveryHeartbeats) {
            transitionTo(LinkState::Connected);
        }
    }

    // Поточний коефіцієнт втрат пакетів у ковзному вікні (0..100 %)
    [[nodiscard]] uint8_t packetLossPercent() const noexcept {
        if (!hasReceivedAny_) return 100;
        size_t received = packetWindow_.count();
        return static_cast<uint8_t>(100 - (received * 100 / packetWindow_.size()));
    }

    // Поточна згладжена затримка передачі
    [[nodiscard]] Milliseconds smoothedRtt() const noexcept {
        return smoothedRtt_;
    }

    // Поточна варіація затримки (джитер)
    [[nodiscard]] Milliseconds rttVariance() const noexcept {
        return rttVariance_;
    }

    // Розрахунок адаптивного таймауту відповіді
    [[nodiscard]] Milliseconds adaptiveTimeout() const noexcept {
        if (smoothedRtt_ == Milliseconds{0}) {
            return config_.failsafeTimeout;
        }
        auto timeout = smoothedRtt_ + (rttVariance_ * 4);
        return std::clamp(timeout, Milliseconds{1000}, config_.failsafeTimeout);
    }

    // Періодичне оновлення внутрішніх таймерів
    LinkState update(TimePoint now = std::chrono::steady_clock::now()) {
        if (!hasReceivedAny_) {
            transitionTo(LinkState::Lost);
            return state_;
        }

        auto dt = std::chrono::duration_cast<Milliseconds>(now - lastHeartbeatTime_);
        uint8_t loss = packetLossPercent();

        if (dt >= config_.failsafeTimeout) {
            consecutiveHeartbeats_ = 0;
            transitionTo(LinkState::Lost);
        } else if (dt >= config_.warningTimeout || loss > config_.lossThresholdPercent) {
            if (state_ != LinkState::Lost) {
                transitionTo(LinkState::Degraded);
            }
        } else {
            if (state_ == LinkState::Degraded) {
                transitionTo(LinkState::Connected);
            }
        }

        return state_;
    }

    [[nodiscard]] LinkState state() const noexcept { return state_; }
    [[nodiscard]] bool isConnected() const noexcept { return state_ == LinkState::Connected; }

private:
    void transitionTo(LinkState newState) {
        if (state_ != newState) {
            LinkState oldState = state_;
            state_ = newState;
            if (stateCallback_) {
                stateCallback_(oldState, newState);
            }
        }
    }

    Config config_;
    LinkState state_;
    TimePoint lastHeartbeatTime_{};
    TimePoint lastAnyPacketTime_{};
    Milliseconds smoothedRtt_{0};
    Milliseconds rttVariance_{0};
    uint8_t lastSequence_{0};
    uint32_t consecutiveHeartbeats_{0};
    std::bitset<64> packetWindow_{};
    bool hasReceivedAny_{false};
    std::function<void(LinkState, LinkState)> stateCallback_;
};
