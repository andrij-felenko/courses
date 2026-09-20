#ifndef HALL_GIMBAL_HPP
#define HALL_GIMBAL_HPP

#include <cstdint>
#include <cmath>
#include <optional>
#include <tuple>

// Параметри калібрування однієї осі джойстика
struct AxisCalibration {
    uint16_t min_raw{200};
    uint16_t center_raw{2048};
    uint16_t max_raw{3900};
};

// Конфігурація драйвера джойстика Холла
struct GimbalConfig {
    AxisCalibration axis_x{};
    AxisCalibration axis_y{};
    float deadzone_radial{0.05f}; // 5% радіальна мертва зона
    float alpha_ema{0.2f};        // Коефіцієнт EMA фільтрації (0.0 < alpha <= 1.0)
};

// Нормовані координати джойстика у діапазоні [-1.0, +1.0]
struct GimbalPosition {
    float x{0.0f};
    float y{0.0f};
    bool valid{true};
};

class HallGimbal {
public:
    explicit HallGimbal(const GimbalConfig& config = {});

    // Оновлення стану при отриманні сирих вимірів АЦП (X, Y)
    GimbalPosition update(uint16_t raw_x, uint16_t raw_y);

    // Автоматичне калібрування нейтралі (поточні виміри вважати центром)
    void calibrateCenter(uint16_t raw_x, uint16_t raw_y);

    // Отримання поточних нормованих координат
    [[nodiscard]] GimbalPosition getPosition() const noexcept { return current_pos_; }

private:
    [[nodiscard]] float normalizeAxis(float raw_val, const AxisCalibration& calib) const noexcept;

    GimbalConfig config_;
    GimbalPosition current_pos_{};

    float filtered_x_{2048.0f};
    float filtered_y_{2048.0f};
    bool is_first_update_{true};
};

#endif // HALL_GIMBAL_HPP
