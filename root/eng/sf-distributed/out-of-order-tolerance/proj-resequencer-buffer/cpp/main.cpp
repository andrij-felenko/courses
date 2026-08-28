#include <iostream>
#include <string>
#include <string_view>
#include <map>
#include <chrono>
#include <functional>
#include <optional>
#include <memory>

class Resequencer {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;
    using DeliverHandler = std::function<void(uint64_t seq, std::string_view payload)>;
    using GapDropHandler = std::function<void(uint64_t lost_seq)>;

    Resequencer(uint64_t start_seq,
                std::chrono::milliseconds gap_timeout,
                size_t max_window_size,
                DeliverHandler on_deliver,
                GapDropHandler on_gap_drop)
        : expected_seq_(start_seq)
        , gap_timeout_(gap_timeout)
        , max_window_size_(max_window_size)
        , on_deliver_(std::move(on_deliver))
        , on_gap_drop_(std::move(on_gap_drop)) {}

    bool push(uint64_t seq, std::string payload) {
        const auto now = Clock::now();

        // 1. Фільтрація старих дублікатів
        if (seq < expected_seq_) {
            return false;
        }

        // 2. Точне вчасне прибуття
        if (seq == expected_seq_) {
            on_deliver_(seq, payload);
            ++expected_seq_;
            flush_continuous_prefix(now);
            return true;
        }

        // 3. Перевірка ліміту вікна буфера
        if (seq >= expected_seq_ + max_window_size_) {
            return false; // Відхилено: надто далеке майбутнє
        }

        // 4. Збереження у відсортованій мапі
        auto [it, inserted] = buffer_.emplace(seq, std::move(payload));
        if (!inserted) {
            return false; // Дублікат уже в буфері
        }

        if (!gap_start_time_.has_value()) {
            gap_start_time_ = now;
        }

        return true;
    }

    void tick() {
        if (!gap_start_time_.has_value()) {
            return;
        }

        const auto now = Clock::now();
        if (now - *gap_start_time_ >= gap_timeout_) {
            // Таймаут очікування: пропускаємо втрачений seq
            on_gap_drop_(expected_seq_);
            ++expected_seq_;
            gap_start_time_.reset();

            flush_continuous_prefix(now);
        }
    }

    [[nodiscard]] uint64_t expected_sequence() const noexcept { return expected_seq_; }
    [[nodiscard]] size_t buffered_count() const noexcept { return buffer_.size(); }

private:
    void flush_continuous_prefix(TimePoint now) {
        while (!buffer_.empty()) {
            auto it = buffer_.begin();
            if (it->first != expected_seq_) {
                break; // Натрапили на наступну прогалину
            }

            on_deliver_(it->first, it->second);
            buffer_.erase(it);
            ++expected_seq_;
        }

        if (!buffer_.empty()) {
            if (!gap_start_time_.has_value()) {
                gap_start_time_ = now;
            }
        } else {
            gap_start_time_.reset();
        }
    }

    uint64_t expected_seq_;
    std::chrono::milliseconds gap_timeout_;
    size_t max_window_size_;
    DeliverHandler on_deliver_;
    GapDropHandler on_gap_drop_;

    std::map<uint64_t, std::string> buffer_;
    std::optional<TimePoint> gap_start_time_;
};
