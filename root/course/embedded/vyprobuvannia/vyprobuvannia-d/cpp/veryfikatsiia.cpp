// Ідіоматичний C++20: шаблонний клас з бітовим вікном
#include <cstdint>
#include <bitset>
#include <optional>

namespace ingest {

template<std::size_t WindowSize = 64>
class SequenceDeduplicator {
public:
    constexpr SequenceDeduplicator() noexcept = default;

    [[nodiscard]] bool process_sequence(uint64_t seq) noexcept {
        if (seq == 0) return false;

        if (!max_seq_seen_.has_value()) {
            max_seq_seen_ = seq;
            window_.reset();
            return true;
        }

        const uint64_t max_seq = *max_seq_seen_;

        if (seq > max_seq) {
            const uint64_t diff = seq - max_seq;
            if (diff < WindowSize) {
                window_ <<= diff;
                window_.set(diff - 1);
            } else {
                window_.reset();
            }
            max_seq_seen_ = seq;
            return true;
        }

        const uint64_t diff = max_seq - seq;
        if (diff == 0 || diff > WindowSize) {
            return false; // Дублікат або вихід за межі вікна
        }

        const std::size_t bit_idx = static_cast<std::size_t>(diff - 1);
        if (window_.test(bit_idx)) {
            return false; // Дублікат
        }

        window_.set(bit_idx);
        return true;
    }

    [[nodiscard]] uint64_t highest_sequence() const noexcept {
        return max_seq_seen_.value_or(0);
    }

private:
    std::optional<uint64_t> max_seq_seen_{std::nullopt};
    std::bitset<WindowSize> window_{0};
};

} // namespace ingest
