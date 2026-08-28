#pragma once

#include <cmath>
#include <vector>
#include <span>
#include <expected>
#include <system_error>
#include <numbers>

enum class ResonantBiquadMode {
    Bandpass,
    PeakingEQ,
    ResonantLowpass
};

enum class BiquadError {
    InvalidSampleRate,
    InvalidCenterFrequency,
    InvalidQualityFactor,
    FrequencyAboveNyquist
};

class ResonantBiquadFilter {
public:
    struct Params {
        float sample_rate{44100.0f};
        float center_freq{1000.0f};
        float Q{1.0f};
        float gain_db{0.0f};
        ResonantBiquadMode mode{ResonantBiquadMode::Bandpass};
    };

    constexpr ResonantBiquadFilter() noexcept = default;

    // Конструктор з ініціалізацією параметрів
    static std::expected<ResonantBiquadFilter, BiquadError> create(const Params& p) {
        ResonantBiquadFilter filter;
        auto result = filter.configure(p);
        if (!result) {
            return std::unexpected(result.error());
        }
        return filter;
    }

    // Налаштувати/змінити параметри резонансу під час роботи
    std::expected<void, BiquadError> configure(const Params& p) {
        if (p.sample_rate <= 0.0f) {
            return std::unexpected(BiquadError::InvalidSampleRate);
        }
        if (p.center_freq <= 0.0f) {
            return std::unexpected(BiquadError::InvalidCenterFrequency);
        }
        if (p.Q <= 0.001f) {
            return std::unexpected(BiquadError::InvalidQualityFactor);
        }
        if (p.center_freq >= p.sample_rate * 0.499f) {
            return std::unexpected(BiquadError::FrequencyAboveNyquist);
        }

        params_ = p;

        const double w0 = 2.0 * std::numbers::pi * static_cast<double>(p.center_freq) / static_cast<double>(p.sample_rate);
        const double alpha = std::sin(w0) / (2.0 * static_cast<double>(p.Q));
        const double cos_w0 = std::cos(w0);
        const double A = std::pow(10.0, static_cast<double>(p.gain_db) / 40.0);

        double b0_raw{0.0}, b1_raw{0.0}, b2_raw{0.0};
        double a0_raw{1.0}, a1_raw{0.0}, a2_raw{0.0};

        switch (p.mode) {
            case ResonantBiquadMode::Bandpass:
                b0_raw = alpha;
                b1_raw = 0.0;
                b2_raw = -alpha;
                a0_raw = 1.0 + alpha;
                a1_raw = -2.0 * cos_w0;
                a2_raw = 1.0 - alpha;
                break;

            case ResonantBiquadMode::PeakingEQ:
                b0_raw = 1.0 + alpha * A;
                b1_raw = -2.0 * cos_w0;
                b2_raw = 1.0 - alpha * A;
                a0_raw = 1.0 + alpha / A;
                a1_raw = -2.0 * cos_w0;
                a2_raw = 1.0 - alpha / A;
                break;

            case ResonantBiquadMode::ResonantLowpass:
                b0_raw = (1.0 - cos_w0) / 2.0;
                b1_raw = 1.0 - cos_w0;
                b2_raw = (1.0 - cos_w0) / 2.0;
                a0_raw = 1.0 + alpha;
                a1_raw = -2.0 * cos_w0;
                a2_raw = 1.0 - alpha;
                break;
        }

        b0_ = static_cast<float>(b0_raw / a0_raw);
        b1_ = static_cast<float>(b1_raw / a0_raw);
        b2_ = static_cast<float>(b2_raw / a0_raw);
        a1_ = static_cast<float>(a1_raw / a0_raw);
        a2_ = static_cast<float>(a2_raw / a0_raw);

        return {};
    }

    // Скидання внутрішньої історії фільтра
    void reset() noexcept {
        z1_ = 0.0f;
        z2_ = 0.0f;
    }

    // Обробка одного відліку в реальному часі (Inlined)
    [[nodiscard]] inline float process_sample(float in_sample) noexcept {
        const float out = b0_ * in_sample + z1_;
        z1_ = b1_ * in_sample - a1_ * out + z2_;
        z2_ = b2_ * in_sample - a2_ * out;
        return out;
    }

    // Обробка буфера через std::span
    void process(std::span<const float> input, std::span<float> output) noexcept {
        const size_t count = std::min(input.size(), output.size());
        for (size_t i = 0; i < count; ++i) {
            output[i] = process_sample(input[i]);
        }
    }

    [[nodiscard]] constexpr const Params& params() const noexcept { return params_; }

private:
    Params params_{};
    float b0_{1.0f}, b1_{0.0f}, b2_{0.0f};
    float a1_{0.0f}, a2_{0.0f};
    float z1_{0.0f}, z2_{0.0f};
};
:::

### 6. Покроковий розбір обчислювальної реалізації

Аналіз ключових архітектурних рішень, прийнятих при розробці API:

1. **Безпека типів у C++23**:
   В інтерфейсі C++ застосовано мовну конструкцію `std::expected<ResonantBiquadFilter, BiquadError>`. Це унеможливлює створення об'єкта фільтра з некоректними чисельним значеннями (наприклад, з резонансною частотою за межею Найквіста або від'ємною добротністю). На відміну від винятків (`exceptions`), використання `std::expected` гарантує відсутність додаткових витрат на розгортання стеку у реальному часі.

2. **Використання `std::span` для нульового копіювання**:
   Приймаючи `std::span<const float>` та `std::span<float>`, метод обробки буфера не виділяє динамічну пам'ять у купі (heap). Фільтр працездатний як з динамічними векторами `std::vector<float>`, так і з фіксованими масивами на стеку `std::array<float, N>` або сумісними аудіобуферами операційних систем.

3. **Оптимізація обчислювального ядра**:
   Обробка одного відліку у функції `biquad_process_sample` потребує всього 5 множень та 4 додавання. Послідовна структура обчислень дозволяє компілятору розгортати цикл обробки буфера (loop unrolling) та застосовувати векторні інструкції SIMD (AVX-256 / NEON) для паралельної обробки декількох аудіоканалів.

### 7. Практичні особливості експлуатації та крайові випадки

1. **Захист від денормалізованих чисел (*Denormal numbers*)**. 
   Якщо на вхід фільтра тривалий час не надходить сигнал (пауза в аудіопотоці), значення елементів затримки `z1` та `z2` починають експоненційно згасати. Перетинаючи межу `1.175494e-38f` (найменше нормалізоване число 32-бітного float), процесор потрапляє у режим обробки денормалів. На багатьох процесорах обробка денормалізованих чисел викликає переключення на мікрокод і сповільнює обчислення у **100–1000 разів**, створюючи пікові зависання аудіопотоку.

   Способи усунення проблеми денормалів:
   - Включення апаратних прапорців пропуску денормалів на рівні процесора:
