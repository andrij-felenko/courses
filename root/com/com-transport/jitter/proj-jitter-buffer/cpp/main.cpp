#include <iostream>
#include <vector>
#include <optional>
#include <span>
#include <cstdint>
#include <algorithm>
#include <chrono>

class AdaptiveJitterBuffer {
public:
    static constexpr size_t BufferCapacity = 64;
    static constexpr uint32_t ClockRateHz = 8000;
    static constexpr uint32_t FrameDurationMs = 20;

    struct Frame {
        uint16_t sequence_number;
        uint32_t timestamp;
        std::chrono::milliseconds arrival_time;
        std::vector<uint8_t> payload;
    };

    explicit AdaptiveJitterBuffer(std::chrono::milliseconds initial_target_delay = std::chrono::milliseconds(40))
        : target_delay_(initial_target_delay),
          slots_(BufferCapacity) {}

    void push_packet(uint16_t seq, uint32_t timestamp,
                     std::span<const uint8_t> payload,
                     std::chrono::milliseconds arrival_time) {
        packets_received_++;

        if (!initialized_) {
            next_play_seq_ = seq;
            initialized_ = true;
        }

        // Перевірка, чи не запізнився пакет остаточно
        if (seq_less(seq, next_play_seq_)) {
            packets_late_dropped_++;
            return;
        }

        // Оцінка затримки проходження та оновлення джитеру
        auto send_time_ms = std::chrono::milliseconds(timestamp / (ClockRateHz / 1000));
        auto transit_time = arrival_time - send_time_ms;

        if (last_transit_time_.has_value()) {
            auto delta = std::abs((transit_time - *last_transit_time_).count());
            // EWMA-фільтр RFC 3550: J_i = J_{i-1} + (|D| - J_{i-1}) / 16
            jitter_q4_ += static_cast<int32_t>(delta) - (jitter_q4_ >> 4);
        }
        last_transit_time_ = transit_time;

        // Адаптивне налаштування глибини буфера
        auto current_jitter_ms = static_cast<uint32_t>(jitter_q4_ >> 4);
        target_delay_ = std::chrono::milliseconds(
            std::clamp(current_jitter_ms * 3 + FrameDurationMs, 20u, 250u)
        );

        // Вставка у чергу
        size_t slot_idx = seq % BufferCapacity;
        slots_[slot_idx] = Frame{
            .sequence_number = seq,
            .timestamp = timestamp,
            .arrival_time = arrival_time,
            .payload = {payload.begin(), payload.end()}
        };
    }

    [[nodiscard]] std::optional<Frame> pop_frame() {
        if (!initialized_) {
            return std::nullopt;
        }

        size_t slot_idx = next_play_seq_ % BufferCapacity;
        auto& slot = slots_[slot_idx];

        if (slot.has_value() && slot->sequence_number == next_play_seq_) {
            Frame result = std::move(*slot);
            slot.reset();
            next_play_seq_++;
            packets_played_++;
            return result;
        }

        // Буферне виснаження: викликається модуль маскування втрат (PLC)
        packets_underrun_++;
        next_play_seq_++;
        return std::nullopt;
    }

    [[nodiscard]] std::chrono::milliseconds target_delay() const noexcept {
        return target_delay_;
    }

private:
    static bool seq_less(uint16_t s1, uint16_t s2) noexcept {
        return static_cast<int16_t>(s1 - s2) < 0;
    }

    std::chrono::milliseconds target_delay_;
    std::vector<std::optional<Frame>> slots_;
    uint16_t next_play_seq_{0};
    int32_t jitter_q4_{0};
    std::optional<std::chrono::milliseconds> last_transit_time_;
    bool initialized_{false};

    uint32_t packets_received_{0};
    uint32_t packets_played_{0};
    uint32_t packets_late_dropped_{0};
    uint32_t packets_underrun_{0};
};
