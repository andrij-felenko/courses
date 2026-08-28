#ifndef LIBFROUDE_HPP
#define LIBFROUDE_HPP

#include <expected>
#include <string_view>
#include <concepts>
#include <span>
#include <cmath>

namespace froude::api {

enum class Error : int {
    InvalidDepth = -1,
    InvalidVelocity = -2,
    InvalidDischarge = -3,
    SubcriticalFlow = -4,
    InvalidScale = -5,
    NullPointer = -6,
    OutOfRange = -7
};

struct FlowInput {
    double velocity_ms{0.0};
    double depth_m{0.0};
    double gravity_ms2{9.80665};
};

struct FlowResult {
    double froude_number{0.0};
    double celerity_ms{0.0};
    bool is_supercritical{false};
};

struct HydraulicJump {
    double h1{0.0};
    double h2{0.0};
    double v1{0.0};
    double v2{0.0};
    double fr1{0.0};
    double fr2{0.0};
    double energy_loss_m{0.0};
};

template<typename T>
concept FloatingPoint = std::is_floating_point_v<T>;

class Calculator {
public:
    template<FloatingPoint T>
    static constexpr std::expected<T, Error> 
    compute_froude(T velocity, T length, T gravity = T(9.80665)) noexcept {
        if (length <= T(0)) return std::unexpected(Error::InvalidDepth);
        if (velocity < T(0)) return std::unexpected(Error::InvalidVelocity);
        if (gravity <= T(0)) return std::unexpected(Error::OutOfRange);

        return velocity / std::sqrt(gravity * length);
    }

    static std::expected<HydraulicJump, Error> 
    compute_jump(double discharge_q, double h1) noexcept;

    static constexpr std::string_view strerror(Error error) noexcept {
        switch (error) {
            case Error::InvalidDepth: return "Invalid depth value (must be > 0)";
            case Error::InvalidVelocity: return "Invalid velocity value (must be >= 0)";
            case Error::InvalidDischarge: return "Invalid discharge value (must be > 0)";
            case Error::SubcriticalFlow: return "Flow is subcritical (Fr <= 1.0)";
            case Error::InvalidScale: return "Invalid scale factor";
            case Error::NullPointer: return "Null pointer passed";
            case Error::OutOfRange: return "Value out of valid physical range";
        }
        return "Unknown froude error";
    }
};

} // namespace froude::api

#endif /* LIBFROUDE_HPP */
