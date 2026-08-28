#include <cstdint>
#include <optional>
#include <bitset>

enum class PacketStatus {
    InOrder,
    GapLoss,
    Reordered,
    Duplicate,
    StaleDrop
};

struct TriageResult {
    PacketStatus status;
    std::uint16_t lost_packets{0};
};

class SequenceTracker {
public:
    constexpr SequenceTracker() noexcept = default;

    TriageResult process(std::uint16_t seq) noexcept {
        if (!initialized_) {
            expected_seq_ = static_cast<std::uint16_t>(seq + 1);
            max_seq_ = seq;
            mask_.set(0);
            initialized_ = true;
            return {PacketStatus::InOrder, 0};
        }

        const auto diff_exp = static_cast<std::int16_t>(seq - expected_seq_);

        // 1. Очікуваний пакет
        if (diff_exp == 0) {
            ++expected_seq_;
            const auto diff_max = static_cast<std::int16_t>(seq - max_seq_);
            if (diff_max > 0) {
                const auto shift = static_cast<std::size_t>(diff_max);
                if (shift < 64) {
                    mask_ <<= shift;
                    mask_.set(0);
                } else {
                    mask_.reset();
                    mask_.set(0);
                }
                max_seq_ = seq;
            }
            return {PacketStatus::InOrder, 0};
        }

        // 2. Випередження черги (пропуск)
        if (diff_exp > 0) {
            const auto diff_max = static_cast<std::int16_t>(seq - max_seq_);
            if (diff_max > 0) {
                const auto shift = static_cast<std::size_t>(diff_max);
                if (shift < 64) {
                    mask_ <<= shift;
                    mask_.set(0);
                } else {
                    mask_.reset();
                    mask_.set(0);
                }
                max_seq_ = seq;
            }
            return {PacketStatus::GapLoss, static_cast<std::uint16_t>(diff_exp)};
        }

        // 3. Минулий номер
        const auto diff_max = static_cast<std::int16_t>(max_seq_ - seq);
        if (diff_max >= 64 || diff_max < 0) {
            return {PacketStatus::StaleDrop, 0};
        }

        if (mask_.test(static_cast<std::size_t>(diff_max))) {
            return {PacketStatus::Duplicate, 0};
        }

        mask_.set(static_cast<std::size_t>(diff_max));
        return {PacketStatus::Reordered, 0};
    }

private:
    std::uint16_t expected_seq_{0};
    std::uint16_t max_seq_{0};
    std::bitset<64> mask_{};
    bool initialized_{false};
};
