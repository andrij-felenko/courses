/**
 * @file event_filter_modern.hpp
 * @brief Шаблонний модуль N-з-M на C++20
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <bit>
#include <concepts>
#include <atomic>
#include <array>

namespace embedded::filter {

/**
 * @brief Шаблонний фільтр N-з-M для вікон M <= 64
 * @tparam M Розмір ковзного вікна в бітах
 * @tparam Non Поріг активації
 * @tparam Noff Поріг деактивації
 * @tparam MaxDwell Максимальний час перебування в стані (0 = вимкнено)
 */
template <std::size_t M, std::size_t Non, std::size_t Noff, std::size_t MaxDwell = 0>
    requires (M >= 1 && M <= 64 && Non <= M && Noff < Non)
class ModernEventFilter final {
public:
    using StorageType = std::conditional_t<(M <= 32), uint32_t, uint64_t>;

    constexpr explicit ModernEventFilter(bool initial_level = false) noexcept
        : history_(initial_level ? Mask : StorageType{0}),
          state_(initial_level),
          dwell_counter_(0),
          glitch_count_(0) {}

    /**
     * @brief Безблокувальний крок оновлення фільтра (O(1))
     */
    [[nodiscard]] bool Update(bool raw_sample) noexcept {
        const StorageType new_bit = raw_sample ? StorageType{1} : StorageType{0};
        const StorageType cur_hist = ((history_.load(std::memory_order_relaxed) << 1) | new_bit) & Mask;
        history_.store(cur_hist, std::memory_order_relaxed);

        const auto ones = static_cast<std::size_t>(std::popcount(cur_hist));
        const bool prev = state_.load(std::memory_order_relaxed);
        bool next = prev;

        if (ones >= Non) {
            next = true;
        } else if (ones <= Noff) {
            next = false;
        }

        if (raw_sample != next) {
            glitch_count_.fetch_add(1, std::memory_order_relaxed);
        }

        if constexpr (MaxDwell > 0) {
            if (next == prev) {
                dwell_counter_.fetch_add(1, std::memory_order_relaxed);
            } else {
                dwell_counter_.store(0, std::memory_order_relaxed);
            }
        }

        state_.store(next, std::memory_order_release);
        return next;
    }

    [[nodiscard]] bool GetState() const noexcept {
        return state_.load(std::memory_order_acquire);
    }

    [[nodiscard]] std::size_t GetCount() const noexcept {
        return static_cast<std::size_t>(std::popcount(history_.load(std::memory_order_relaxed)));
    }

    [[nodiscard]] uint32_t GetGlitches() const noexcept {
        return glitch_count_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] bool IsStuck() const noexcept {
        if constexpr (MaxDwell > 0) {
            return dwell_counter_.load(std::memory_order_relaxed) >= MaxDwell;
        } else {
            return false;
        }
    }

private:
    static constexpr StorageType ComputeMask() noexcept {
        if constexpr (M == sizeof(StorageType) * 8) {
            return ~StorageType{0};
        } else {
            return (StorageType{1} << M) - StorageType{1};
        }
    }

    static constexpr StorageType Mask = ComputeMask();

    std::atomic<StorageType> history_{0};
    std::atomic<bool>        state_{false};
    std::atomic<std::size_t> dwell_counter_{0};
    std::atomic<uint32_t>    glitch_count_{0};
};

} // namespace embedded::filter
