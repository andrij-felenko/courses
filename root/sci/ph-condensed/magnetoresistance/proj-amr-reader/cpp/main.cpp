// C++17/C++20 Implementation: RAII клас драйвера AMR-магнітометра
#include <iostream>
#include <cmath>
#include <array>
#include <optional>
#include <numbers>

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3f operator-(const Vector3f& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
};

struct CalibrationData {
    Vector3f hard_iron_offset{0.0f, 0.0f, 0.0f};
    std::array<std::array<float, 3>, 3> soft_iron_matrix{{{1,0,0}, {0,1,0}, {0,0,1}}};
    float sensitivity_lsb_per_uT{3000.0f};
};

class AmrSensorReader {
public:
    explicit AmrSensorReader(uint8_t i2c_address, CalibrationData cal)
        : i2c_addr_(i2c_address), cal_(std::move(cal)) {}

    // Зчитування диференціального вектора із Set/Reset імпульсом
    std::optional<Vector3f> read_differential_raw() const {
        auto set_val = read_single_pulse(PulseType::Set);
        if (!set_val) return std::nullopt;

        auto reset_val = read_single_pulse(PulseType::Reset);
        if (!reset_val) return std::nullopt;

        return Vector3f{
            (set_val->x - reset_val->x) / 2.0f,
            (set_val->y - reset_val->y) / 2.0f,
            (set_val->z - reset_val->z) / 2.0f
        };
    }

    // Обчислення фізичного вектору магнітного поля (мкТл) та азимуту
    std::pair<Vector3f, float> process(const Vector3f& raw) const noexcept {
        const Vector3f centered = (raw - cal_.hard_iron_offset);
        const float dx = centered.x / cal_.sensitivity_lsb_per_uT;
        const float dy = centered.y / cal_.sensitivity_lsb_per_uT;
        const float dz = centered.z / cal_.sensitivity_lsb_per_uT;

        const auto& m = cal_.soft_iron_matrix;
        Vector3f b_field{
            m[0][0] * dx + m[0][1] * dy + m[0][2] * dz,
            m[1][0] * dx + m[1][1] * dy + m[1][2] * dz,
            m[2][0] * dx + m[2][1] * dy + m[2][2] * dz
        };

        float heading_deg = std::atan2(b_field.y, b_field.x) * (180.0f / std::numbers::pi_v<float>);
        if (heading_deg < 0.0f) {
            heading_deg += 360.0f;
        }

        return {b_field, heading_deg};
    }

private:
    enum class PulseType { Set, Reset };

    std::optional<Vector3f> read_single_pulse(PulseType type) const {
        // У реальному коді тут відбувається виклик I2C шини
        uint8_t pulse_cmd = (type == PulseType::Set) ? 0x08 : 0x10;
        (void)pulse_cmd;
        // Симуляція відгуку АЦП
        return Vector3f{1024.0f, -512.0f, 2048.0f};
    }

    uint8_t i2c_addr_;
    CalibrationData cal_;
};
