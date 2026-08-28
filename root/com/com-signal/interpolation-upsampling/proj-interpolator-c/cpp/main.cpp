// C++20: Поліфазний інтерполятор із шаблонізацією типу відліків та RAII
#include <vector>
#include <span>
#include <cstdint>
#include <concepts>
#include <stdexcept>
#include <algorithm>

template <typename T = float>
class PolyphaseInterpolator {
public:
    PolyphaseInterpolator(size_t factor_L, std::span<const T> filter_taps)
        : factor_L_(factor_L) {
        if (factor_L_ == 0 || filter_taps.empty()) {
            throw std::invalid_argument("Некоректні параметри інтерполятора");
        }

        taps_per_phase_ = (filter_taps.size() + factor_L_ - 1) / factor_L_;
        phase_taps_.resize(factor_L_, std::vector<T>(taps_per_phase_, T{0}));

        // Декомпозиція коефіцієнтів h[n*L + p]
        for (size_t i = 0; i < filter_taps.size(); ++i) {
            size_t p = i % factor_L_;
            size_t n = i / factor_L_;
            phase_taps_[p][n] = filter_taps[i];
        }

        state_buffer_.resize(taps_per_phase_, T{0});
    }

    // Обробка одного відліку -> повертає std::vector із L інтерпольованих відліків
    std::vector<T> process_sample(T input_sample) {
        state_buffer_[state_head_] = input_sample;
        std::vector<T> output(factor_L_);

        for (size_t p = 0; p < factor_L_; ++p) {
            T acc{0};
            const auto& phase_h = phase_taps_[p];

            for (size_t i = 0; i < taps_per_phase_; ++i) {
                size_t idx = (state_head_ + taps_per_phase_ - i) % taps_per_phase_;
                acc += phase_h[i] * state_buffer_[idx];
            }
            output[p] = acc;
        }

        state_head_ = (state_head_ + 1) % taps_per_phase_;
        return output;
    }

    // Заповнення наданого буфера без додаткових виділень пам'яті
    void process_sample(T input_sample, std::span<T> output_span) {
        if (output_span.size() < factor_L_) {
            throw std::out_of_range("Вихідний буфер замалий для фаз L");
        }
        state_buffer_[state_head_] = input_sample;

        for (size_t p = 0; p < factor_L_; ++p) {
            T acc{0};
            const auto& phase_h = phase_taps_[p];

            for (size_t i = 0; i < taps_per_phase_; ++i) {
                size_t idx = (state_head_ + taps_per_phase_ - i) % taps_per_phase_;
                acc += phase_h[i] * state_buffer_[idx];
            }
            output_span[p] = acc;
        }

        state_head_ = (state_head_ + 1) % taps_per_phase_;
    }

    [[nodiscard]] size_t factor() const noexcept { return factor_L_; }

private:
    size_t factor_L_{1};
    size_t taps_per_phase_{0};
    size_t state_head_{0};
    std::vector<std::vector<T>> phase_taps_;
    std::vector<T> state_buffer_;
};
