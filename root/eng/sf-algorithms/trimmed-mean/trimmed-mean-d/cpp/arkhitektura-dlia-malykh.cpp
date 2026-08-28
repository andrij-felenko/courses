#include <algorithm>
#include <array>
#include <cstddef>
#include <numeric>

template <std::size_t WindowSize, std::size_t TrimK>
requires (2 * TrimK < WindowSize)
class SlidingTrimmedMeanFilter {
public:
    constexpr SlidingTrimmedMeanFilter() = default;

    [[nodiscard]] double update(double new_val) noexcept {
        if (count_ < WindowSize) {
            buffer_[head_] = new_val;
            head_ = (head_ + 1) % WindowSize;

            auto it = std::upper_bound(sorted_.begin(), sorted_.begin() + count_, new_val);
            std::move_backward(it, sorted_.begin() + count_, sorted_.begin() + count_ + 1);
            *it = new_val;
            ++count_;
        } else {
            const double old_val = buffer_[head_];
            buffer_[head_] = new_val;
            head_ = (head_ + 1) % WindowSize;

            /* Пошук і вилучення старого елемента */
            auto old_it = std::lower_bound(sorted_.begin(), sorted_.end(), old_val);
            std::move(old_it + 1, sorted_.end(), old_it);

            /* Вставка нового елемента */
            auto new_it = std::upper_bound(sorted_.begin(), sorted_.end() - 1, new_val);
            std::move_backward(new_it, sorted_.end() - 1, sorted_.end());
            *new_it = new_val;
        }

        if (count_ <= 2 * TrimK) {
            const double sum = std::accumulate(sorted_.begin(), sorted_.begin() + count_, 0.0);
            return sum / static_cast<double>(count_);
        }

        const auto start_it = sorted_.begin() + TrimK;
        const auto end_it = sorted_.begin() + (count_ - TrimK);
        const double core_sum = std::accumulate(start_it, end_it, 0.0);
        return core_sum / static_cast<double>(count_ - 2 * TrimK);
    }

    [[nodiscard]] constexpr std::size_t size() const noexcept { return count_; }
    constexpr void reset() noexcept { count_ = 0; head_ = 0; }

private:
    std::array<double, WindowSize> buffer_{};
    std::array<double, WindowSize> sorted_{};
    std::size_t head_{0};
    std::size_t count_{0};
};
