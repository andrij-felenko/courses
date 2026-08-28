#include <cstdint>
#include <vector>
#include <optional>
#include <chrono>
#include <span>
#include <algorithm>

template <typename PayloadType, std::size_t Capacity = 64>
class ReorderBuffer {
public:
    struct Packet {
        std::uint32_t sequence{0};
        std::chrono::steady_clock::time_point arrival_time{};
        PayloadType payload{};
    };

    explicit ReorderBuffer(std::chrono::milliseconds gap_timeout) noexcept
        : gap_timeout_(gap_timeout) {
        slots_.resize(Capacity);
    }

    bool push(std::uint32_t seq, PayloadType payload,
              std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now()) {
        if (!initialized_) {
            expected_seq_ = seq;
            initialized_ = true;
        }

        const auto diff = static_cast<std::int32_t>(seq - expected_seq_);
        if (diff < 0 || static_cast<std::size_t>(diff) >= Capacity) {
            return false; // Старий номер, дублікат або вихід за межі вікна
        }

        const std::size_t idx = seq % Capacity;
        if (slots_[idx].has_value() && slots_[idx]->sequence == seq) {
            return false; // Дублікат уже в буфері
        }

        slots_[idx] = Packet{
            .sequence = seq,
            .arrival_time = now,
            .payload = std::move(payload)
        };
        return true;
    }

    [[nodiscard]] std::optional<Packet> pop() noexcept {
        if (!initialized_) {
            return std::nullopt;
        }

        const std::size_t idx = expected_seq_ % Capacity;
        if (slots_[idx].has_value() && slots_[idx]->sequence == expected_seq_) {
            Packet ready = std::move(*slots_[idx]);
            slots_[idx].reset();
            ++expected_seq_;
            gap_start_time_.reset();
            return ready;
        }

        return std::nullopt;
    }

    void check_timeout(std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now()) noexcept {
        if (!initialized_) {
            return;
        }

        const std::size_t idx = expected_seq_ % Capacity;
        if (slots_[idx].has_value()) {
            return;
        }

        const bool has_future = std::any_of(slots_.begin(), slots_.end(),
            [](const auto& s) noexcept { return s.has_value(); });

        if (!has_future) {
            gap_start_time_.reset();
            return;
        }

        if (!gap_start_time_.has_value()) {
            gap_start_time_ = now;
        } else if (now - *gap_start_time_ >= gap_timeout_) {
            // Пропускаємо втрачений пакет через таймаут
            ++expected_seq_;
            gap_start_time_.reset();
        }
    }

    [[nodiscard]] std::uint32_t expected_sequence() const noexcept {
        return expected_seq_;
    }

private:
    std::vector<std::optional<Packet>> slots_;
    std::uint32_t expected_seq_{0};
    std::chrono::milliseconds gap_timeout_;
    std::optional<std::chrono::steady_clock::time_point> gap_start_time_{};
    bool initialized_{false};
};
