#pragma once

#include <optional>

namespace fc {

// Комплементарний фільтр: швидкість інтегруємо з акселерометра (швидко,
// але спливає), позицію підтягуємо барометром (повільно, зате без дрейфу).
class AltitudeFusion {
public:
    constexpr AltitudeFusion(float k_alt, float k_climb) noexcept
        : k_alt_{k_alt}, k_climb_{k_climb} {}

    // baro = std::nullopt, коли свіжого відліку барометра нема.
    void update(std::optional<float> baro_alt, float acc_up, float dt) noexcept;

    [[nodiscard]] float altitude() const noexcept { return alt_; }
    [[nodiscard]] float climb_rate() const noexcept { return climb_; }
    [[nodiscard]] bool primed() const noexcept { return primed_; }
    [[nodiscard]] unsigned rejected() const noexcept { return rejected_; }

private:
    float k_alt_;
    float k_climb_;
    float alt_{0.0f};
    float climb_{0.0f};
    float spike_limit_{15.0f};   // м, поріг відкидання викидів баро
    bool primed_{false};
    unsigned rejected_{0};
};

}  // namespace fc
