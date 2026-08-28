#include <cstdint>
#include <concepts>
#include <optional>
#include <atomic>
#include <string_view>

enum class ReplayStatus {
    Accepted,
    Duplicate,
    Stale
};

template <std::size_t WindowSize = 64>
requires (WindowSize == 64) // Для розширених розмірів використовується блоковий масив слів
class AntiReplayWindow {
public:
    constexpr AntiReplayWindow() noexcept = default;

    [[nodiscard]] ReplayStatus process(uint64_t seq) noexcept {
        // Обробка найпершого пакета після запуску сесії
        if (accepted_count_ == 0 && max_seq_ == 0 && bitmap_ == 0) {
            max_seq_ = seq;
            bitmap_ = 1ULL;
            ++accepted_count_;
            return ReplayStatus::Accepted;
        }

        // Сценарій 1: Новий максимальний порядковий номер (просування вікна)
        if (seq > max_seq_) {
            const uint64_t diff = seq - max_seq_;
            if (diff < WindowSize) {
                bitmap_ = (bitmap_ << diff) | 1ULL;
            } else {
                bitmap_ = 1ULL; // Повне витіснення попереднього діапазону
            }
            max_seq_ = seq;
            ++accepted_count_;
            return ReplayStatus::Accepted;
        }

        // Сценарій 2: Застарілий номер за межами лівої межі активного вікна
        const uint64_t diff = max_seq_ - seq;
        if (diff >= WindowSize) {
            ++stale_count_;
            return ReplayStatus::Stale;
        }

        // Сценарій 3: Номер усередині активного ковзного вікна
        const uint64_t bit_mask = 1ULL << diff;
        if ((bitmap_ & bit_mask) != 0) {
            ++duplicate_count_;
            return ReplayStatus::Duplicate;
        }

        bitmap_ |= bit_mask;
        ++accepted_count_;
        return ReplayStatus::Accepted;
    }

    [[nodiscard]] uint64_t max_sequence() const noexcept { return max_seq_; }
    [[nodiscard]] uint64_t accepted_count() const noexcept { return accepted_count_; }
    [[nodiscard]] uint64_t duplicate_count() const noexcept { return duplicate_count_; }
    [[nodiscard]] uint64_t stale_count() const noexcept { return stale_count_; }

private:
    uint64_t max_seq_{0};
    uint64_t bitmap_{0};
    uint64_t accepted_count_{0};
    uint64_t duplicate_count_{0};
    uint64_t stale_count_{0};
};
