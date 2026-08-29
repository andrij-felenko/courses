#pragma once

namespace hitl {

// Монітор розкачки: прибирає повільний тренд, міряє огинаючу амплітуду
// коливальної складової та її частоту за переходами через нуль. Смуга
// людського контуру — 0.5–2.5 Гц; вище лежать вібрації рами й помилки
// бортового D-терма, нижче — звичайні маневри.
class PioMonitor {
public:
    explicit PioMonitor(float dt) noexcept : dt_{dt} {}

    void Update(float x) noexcept;

    [[nodiscard]] float oscillation() const noexcept { return hp_; }
    [[nodiscard]] float amplitude() const noexcept { return amp_; }
    [[nodiscard]] float frequency_hz() const noexcept { return freq_hz_; }
    [[nodiscard]] float growth() const noexcept;
    [[nodiscard]] bool IsPio(float amp_threshold) const noexcept;

private:
    float dt_;
    float trend_{0.0f};
    float hp_{0.0f};
    float amp_{0.0f};
    float freq_hz_{0.0f};
    int crossings_{0};
    int sign_{0};
    float window_t_{0.0f};
    float amp_first_{0.0f};
    float amp_last_{0.0f};
    bool seeded_{false};
};

// Взаємна кореляція стіка й гіроскопа на нульовому зсуві: близьке до -1
// означає строгу протифазу, тобто оператор підкачує енергію в коливання.
class PioCorrelator {
public:
    PioCorrelator(float dt, float window_sec);

    void Update(float a, float b) noexcept;
    [[nodiscard]] float value() const noexcept;

private:
    float leak_;
    float sxy_{0.0f};
    float sxx_{0.0f};
    float syy_{0.0f};
};

// Аналітичний бюджет фази: скільки градусів запасу з'їдає чиста затримка.
[[nodiscard]] float PhaseMargin(float pm0_deg, float omega_c, float tau) noexcept;
[[nodiscard]] float CriticalDelay(float pm0_deg, float omega_c) noexcept;

}  // namespace hitl
