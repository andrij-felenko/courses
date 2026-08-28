#include <cstdint>
#include <cstddef>
#include <array>
#include <iostream>
#include <cassert>

enum class ReplayStatus : uint8_t {
    Ok = 0,
    Duplicate = 1,
    TooOld = 2
};

template <size_t WindowWords = 2>
class ReplayWindow {
public:
    static constexpr size_t BitsPerWord = 64;
    static constexpr size_t TotalBits = WindowWords * BitsPerWord;

    constexpr ReplayWindow() noexcept {
        reset();
    }

    void reset() noexcept {
        seq_max_ = 0;
        bitmap_.fill(0);
    }

    // Фаза 1: Перевірка без зміни стану (перед перевіркою AEAD/HMAC)
    [[nodiscard]] ReplayStatus check(uint64_t seq) const noexcept {
        if (seq == 0) {
            return ReplayStatus::TooOld;
        }

        if (seq > seq_max_) {
            return ReplayStatus::Ok;
        }

        const uint64_t diff = seq_max_ - seq;
        if (diff >= TotalBits) {
            return ReplayStatus::TooOld;
        }

        const size_t word_idx = diff / BitsPerWord;
        const size_t bit_idx = diff % BitsPerWord;

        if ((bitmap_[word_idx] & (uint64_t{1} << bit_idx)) != 0) {
            return ReplayStatus::Duplicate;
        }

        return ReplayStatus::Ok;
    }

    // Фаза 2: Фіксація пакета після успішної криптографічної перевірки
    void commit(uint64_t seq) noexcept {
        if (seq > seq_max_) {
            const uint64_t diff = seq - seq_max_;
            if (diff < TotalBits) {
                const size_t word_shift = diff / BitsPerWord;
                const size_t bit_shift = diff % BitsPerWord;

                for (int i = static_cast<int>(WindowWords) - 1; i >= 0; --i) {
                    const int src = i - static_cast<int>(word_shift);
                    uint64_t val = (src >= 0) ? (bitmap_[src] << bit_shift) : 0;
                    if (src > 0 && bit_shift > 0) {
                        val |= (bitmap_[src - 1] >> (BitsPerWord - bit_shift));
                    }
                    bitmap_[i] = val;
                }
            } else {
                bitmap_.fill(0);
            }

            seq_max_ = seq;
            bitmap_[0] |= uint64_t{1};
        } else {
            const uint64_t diff = seq_max_ - seq;
            if (diff < TotalBits) {
                const size_t word_idx = diff / BitsPerWord;
                const size_t bit_idx = diff % BitsPerWord;
                bitmap_[word_idx] |= (uint64_t{1} << bit_idx);
            }
        }
    }

    [[nodiscard]] uint64_t max_sequence() const noexcept {
        return seq_max_;
    }

private:
    uint64_t seq_max_{0};
    std::array<uint64_t, WindowWords> bitmap_{};
};
