// cpp_colorimetry.hpp - Об'єктно-орієнтований C++20 інтерфейс
#ifndef CPP_COLORIMETRY_HPP
#define CPP_COLORIMETRY_HPP

#include <vector>
#include <array>
#include <span>
#include <expected>
#include <cstdint>
#include <string_view>

namespace colorimetry {

constexpr uint16_t MinWavelengthNm = 380;
constexpr uint16_t MaxWavelengthNm = 780;
constexpr size_t   CriSampleCount  = 15;

enum class ErrorCode : int32_t {
    NullPointer       = -1,
    InvalidWavelength = -2,
    InvalidStep       = -3,
    ZeroIntegral      = -4,
    OutOfRange        = -5
};

struct SpectralData {
    uint16_t start_wavelength_nm{380};
    uint16_t step_wavelength_nm{5};
    std::vector<double> power_values{};

    [[nodiscard]] bool is_valid() const noexcept {
        if (power_values.empty() || (step_wavelength_nm != 1 && step_wavelength_nm != 5)) {
            return false;
        }
        const auto end_wl = start_wavelength_nm + (power_values.size() - 1) * step_wavelength_nm;
        return start_wavelength_nm <= MinWavelengthNm && end_wl >= MaxWavelengthNm;
    }
};

struct TristimulusXYZ {
    double X{0.0};
    double Y{0.0};
    double Z{0.0};
};

struct ChromaticityCoords {
    double x{0.0};
    double y{0.0};
    double u_prime{0.0};
    double v_prime{0.0};
};

struct CCTResult {
    double cct_kelvin{0.0};
    double duv{0.0};
    bool   is_valid{false};
};

struct CRIResult {
    double R_a{0.0};
    std::array<double, CriSampleCount> R_i{};
    double R_9{0.0};
};

} // namespace colorimetry

#endif // CPP_COLORIMETRY_HPP
