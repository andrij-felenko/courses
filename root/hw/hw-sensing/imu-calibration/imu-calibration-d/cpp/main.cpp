#include <array>
#include <span>
#include <cstdint>
#include <cstring>
#include <algorithm>

namespace imu {

inline constexpr uint32_t MagicIdentifier = 0x494D5543; // "IMUC"
inline constexpr uint16_t SchemaVersion   = 2;

using Vector3f = std::array<float, 3>;
using Matrix3f = std::array<std::array<float, 3>, 3>;

struct TemperaturePoly {
    Vector3f c0{};    // Вільний член полінома (зсув при T0)
    Vector3f c1{};    // Лінійний коефіцієнт (1/°C)
    Vector3f c2{};    // Квадратичний коефіцієнт (1/°C²)
    Vector3f c3{};    // Кубічний коефіцієнт (1/°C³)
    float    t0{25.0f}; // Базова температура калібрування, °C

    [[nodiscard]] constexpr Vector3f evaluate(float temp_c) const noexcept {
        const float dt = temp_c - t0;
        return {
            c0[0] + dt * (c1[0] + dt * (c2[0] + dt * c3[0])),
            c0[1] + dt * (c1[1] + dt * (c2[1] + dt * c3[1])),
            c0[2] + dt * (c1[2] + dt * (c2[2] + dt * c3[2]))
        };
    }
};

struct alignas(4) CalibrationProfile {
    uint32_t        magic{MagicIdentifier};
    uint16_t        version{SchemaVersion};
    uint16_t        reserved{0};
    
    Matrix3f        accel_matrix{Matrix3f{{{1.0f, 0.0f, 0.0f}, {0.0f, 1.0f, 0.0f}, {0.0f, 0.0f, 1.0f}}}};
    Vector3f        accel_bias{};
    
    Matrix3f        gyro_matrix{Matrix3f{{{1.0f, 0.0f, 0.0f}, {0.0f, 1.0f, 0.0f}, {0.0f, 0.0f, 1.0f}}}};
    TemperaturePoly gyro_poly{};
    
    uint32_t        crc32{0};

    [[nodiscard]] static uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (const uint8_t byte : data) {
            crc ^= byte;
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
            }
        }
        return ~crc;
    }

    void update_checksum() noexcept {
        const auto bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(this),
                                                   sizeof(CalibrationProfile) - sizeof(uint32_t));
        crc32 = calculate_crc32(bytes);
    }

    [[nodiscard]] bool is_valid() const noexcept {
        if (magic != MagicIdentifier || version != SchemaVersion) {
            return false;
        }
        const auto bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(this),
                                                   sizeof(CalibrationProfile) - sizeof(uint32_t));
        return crc32 == calculate_crc32(bytes);
    }
};

class Calibrator {
public:
    explicit Calibrator(CalibrationProfile profile = {}) noexcept : profile_{profile} {
        if (!profile_.is_valid()) {
            profile_ = CalibrationProfile{};
            profile_.update_checksum();
        }
    }

    [[nodiscard]] Vector3f correct_accelerometer(const Vector3f& raw) const noexcept {
        const float zx = raw[0] - profile_.accel_bias[0];
        const float zy = raw[1] - profile_.accel_bias[1];
        const float zz = raw[2] - profile_.accel_bias[2];

        return {
            profile_.accel_matrix[0][0] * zx + profile_.accel_matrix[0][1] * zy + profile_.accel_matrix[0][2] * zz,
            profile_.accel_matrix[1][0] * zx + profile_.accel_matrix[1][1] * zy + profile_.accel_matrix[1][2] * zz,
            profile_.accel_matrix[2][0] * zx + profile_.accel_matrix[2][1] * zy + profile_.accel_matrix[2][2] * zz
        };
    }

    [[nodiscard]] Vector3f correct_gyroscope(const Vector3f& raw, float temp_c) const noexcept {
        const Vector3f bias = profile_.gyro_poly.evaluate(temp_c);
        
        const float zx = raw[0] - bias[0];
        const float zy = raw[1] - bias[1];
        const float zz = raw[2] - bias[2];

        return {
            profile_.gyro_matrix[0][0] * zx + profile_.gyro_matrix[0][1] * zy + profile_.gyro_matrix[0][2] * zz,
            profile_.gyro_matrix[1][0] * zx + profile_.gyro_matrix[1][1] * zy + profile_.gyro_matrix[1][2] * zz,
            profile_.gyro_matrix[2][0] * zx + profile_.gyro_matrix[2][1] * zy + profile_.gyro_matrix[2][2] * zz
        };
    }

    [[nodiscard]] const CalibrationProfile& profile() const noexcept { return profile_; }
    void set_profile(const CalibrationProfile& profile) noexcept { profile_ = profile; }

private:
    CalibrationProfile profile_{};
};

} // namespace imu
