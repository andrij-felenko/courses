#include <array>
#include <optional>
#include <algorithm>
#include <cstddef>
#include <cstdint>

class NowCastFilter {
public:
    static constexpr std::size_t WindowHours = 12;

    struct Sample {
        float concentration{0.0f};
        bool valid{false};
    };

    constexpr NowCastFilter() noexcept = default;

    // Додавання нового погодинного вимірювання
    void push(float concentration, bool is_valid = true) noexcept {
        head_ = (head_ + WindowHours - 1) % WindowHours;
        buffer_[head_] = Sample{is_valid ? concentration : 0.0f, is_valid};
        if (count_ < WindowHours) {
            count_++;
        }
    }

    // Обчислення NowCast з поверненням std::optional
    [[nodiscard]] std::optional<float> calculate() const noexcept {
        if (count_ == 0) return std::nullopt;

        // Перевірка умови EPA: щонайменше 2 з останніх 3 годин мають бути валідними
        std::size_t recent_valid = 0;
        const std::size_t check_limit = std::min<std::size_t>(count_, 3);
        for (std::size_t i = 0; i < check_limit; ++i) {
            if (get_sample(i).valid) recent_valid++;
        }
        if (recent_valid < 2 && count_ >= 3) return std::nullopt;

        // Пошук екстремумів серед валідних елементів
        float c_min = 1e9f;
        float c_max = -1.0f;
        std::size_t total_valid = 0;

        for (std::size_t i = 0; i < count_; ++i) {
            const auto& s = get_sample(i);
            if (s.valid) {
                c_min = std::min(c_min, s.concentration);
                c_max = std::max(c_max, s.concentration);
                total_valid++;
            }
        }

        if (total_valid == 0) return std::nullopt;

        // Розрахунок коефіцієнта зважування w
        float w = 1.0f;
        if (c_max > 0.0f) {
            w = std::max(c_min / c_max, 0.5f);
        }

        // Обчислення адаптивної зваженої суми
        float sum_weighted_conc = 0.0f;
        float sum_weights = 0.0f;
        float current_weight = 1.0f;

        for (std::size_t i = 0; i < count_; ++i) {
            const auto& s = get_sample(i);
            if (s.valid) {
                sum_weighted_conc += s.concentration * current_weight;
                sum_weights += current_weight;
            }
            current_weight *= w;
        }

        if (sum_weights <= 0.0f) return std::nullopt;
        return sum_weighted_conc / sum_weights;
    }

    // Скидання внутрішнього стану
    void reset() noexcept {
        head_ = 0;
        count_ = 0;
        buffer_.fill(Sample{});
    }

    [[nodiscard]] std::size_t count() const noexcept { return count_; }

private:
    [[nodiscard]] const Sample& get_sample(std::size_t hour_offset) const noexcept {
        return buffer_[(head_ + hour_offset) % WindowHours];
    }

    std::array<Sample, WindowHours> buffer_{};
    std::size_t head_{0};
    std::size_t count_{0};
};
