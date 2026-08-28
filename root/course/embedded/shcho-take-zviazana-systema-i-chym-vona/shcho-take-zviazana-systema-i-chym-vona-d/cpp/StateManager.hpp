/*
 * StateManager.hpp
 * Менеджер розподіленого стану IoT-вузла на сучасному C++20.
 * Типобезпечний, RAII, без витоків пам'яті та винятків у вбудованому коді.
 */

#pragma once

#include <cstdint>
#include <array>
#include <span>
#include <string_view>
#include <optional>
#include <algorithm>

namespace iot {

enum class ConnectionState : uint8_t {
    Disconnected,
    Connecting,
    Connected,
    Syncing
};

struct NodeConfig {
    float targetTemperature{20.0f};
    uint16_t fanSpeedRpm{1000};
    bool heatingEnabled{false};
    uint32_t sequenceId{0};

    [[nodiscard]] constexpr bool isValid() const noexcept {
        return (targetTemperature >= 5.0f && targetTemperature <= 40.0f) &&
               (fanSpeedRpm <= 3000);
    }
};

struct TelemetryEntry {
    uint32_t timestamp{0};
    float measuredTemperature{0.0f};
    uint16_t currentPowerWatts{0};
    uint8_t flags{0};
};

template <size_t QueueCapacity = 32>
class OfflineTelemetryQueue {
public:
    constexpr OfflineTelemetryQueue() noexcept = default;

    void push(const TelemetryEntry& entry) noexcept {
        buffer_[head_] = entry;
        head_ = (head_ + 1) % QueueCapacity;
        if (count_ < QueueCapacity) {
            ++count_;
        } else {
            tail_ = (tail_ + 1) % QueueCapacity;
        }
    }

    [[nodiscard]] std::optional<TelemetryEntry> pop() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        TelemetryEntry item = buffer_[tail_];
        tail_ = (tail_ + 1) % QueueCapacity;
        --count_;
        return item;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }

private:
    std::array<TelemetryEntry, QueueCapacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
};

class EdgeStateManager {
public:
    explicit EdgeStateManager(const NodeConfig& initialConfig) noexcept
        : desiredConfig_{initialConfig},
          reportedConfig_{initialConfig},
          activeHardware_{initialConfig} {}

    [[nodiscard]] ConnectionState connectionState() const noexcept { return connState_; }
    void setConnectionState(ConnectionState newState) noexcept { connState_ = newState; }

    void recordTelemetry(const TelemetryEntry& entry) noexcept {
        queue_.push(entry);
    }

    [[nodiscard]] std::optional<TelemetryEntry> fetchPendingTelemetry() noexcept {
        return queue_.pop();
    }

    /* Застосування дельти від хмарного Digital Twin */
    [[nodiscard]] bool applyDesiredDelta(const NodeConfig& newDesired) noexcept {
        if (newDesired.sequenceId <= reportedConfig_.sequenceId) {
            return false; /* Ігнорування застарілої або дубльованої версії */
        }
        if (!newDesired.isValid()) {
            return false; /* Відхилення небезпечних фізичних параметрів */
        }

        desiredConfig_ = newDesired;
        deltaPending_ = true;
        return true;
    }

    /* Узгодження фізичного стану обладнання */
    void reconcileHardware() noexcept {
        if (!deltaPending_) return;

        /* Фізичне застосування конфігурації до апаратних драйверів */
        activeHardware_ = desiredConfig_;
        reportedConfig_ = activeHardware_;
        deltaPending_ = false;
    }

    [[nodiscard]] const NodeConfig& reportedState() const noexcept { return reportedConfig_; }
    [[nodiscard]] bool isDeltaPending() const noexcept { return deltaPending_; }
    [[nodiscard]] size_t bufferedTelemetryCount() const noexcept { return queue_.size(); }

private:
    NodeConfig desiredConfig_{};
    NodeConfig reportedConfig_{};
    NodeConfig activeHardware_{};
    OfflineTelemetryQueue<32> queue_{};
    ConnectionState connState_{ConnectionState::Disconnected};
    bool deltaPending_{false};
};

} // namespace iot
