// igrf_model.hpp - Ідіоматичний C++ API геомагнітної моделі IGRF
#ifndef IGRF_MODEL_HPP
#define IGRF_MODEL_HPP

#include <cmath>
#include <vector>
#include <array>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>

namespace geodynamo::igrf {

constexpr std::size_t MaxDegree = 13;
constexpr double EarthRadiusKm = 6371.2;

struct GeodeticCoord {
    double latitude_deg{0.0};
    double longitude_deg{0.0};
    double altitude_km{0.0};
    double epoch_year{2025.0};
};

struct MagneticVector {
    double X_nT{0.0};
    double Y_nT{0.0};
    double Z_nT{0.0};
    double H_nT{0.0};
    double F_nT{0.0};
    double D_deg{0.0};
    double I_deg{0.0};
};

enum class IGRFError {
    InvalidLatitude,
    InvalidLongitude,
    InvalidEpoch,
    FileNotFound,
    ParseError
};

class IGRFModel {
public:
    using Matrix = std::array<std::array<double, MaxDegree + 1>, MaxDegree + 1>;

    IGRFModel() = default;

    // Завантаження коефіцієнтів з текстового файлу IGRF.COF / igrf13.f
    [[nodiscard]] static std::expected<IGRFModel, IGRFError> load_from_file(std::string_view filepath);

    // Встановлення коефіцієнтів напряму
    void set_coefficients(double epoch, const Matrix& g, const Matrix& h) noexcept {
        epoch_ = epoch;
        g_ = g;
        h_ = h;
    }

    // Обчислення геомагнітного вектора
    [[nodiscard]] std::expected<MagneticVector, IGRFError> evaluate(const GeodeticCoord& coord) const noexcept;

private:
    double epoch_{2025.0};
    Matrix g_{};
    Matrix h_{};

    // Нормалізовані приєднані поліноми Лежандра та їхні похідні
    void compute_legendre(double costheta, double sintheta, 
                          std::array<std::array<double, MaxDegree + 1>, MaxDegree + 1>& P,
                          std::array<std::array<double, MaxDegree + 1>, MaxDegree + 1>& dP) const noexcept;
};

} // namespace geodynamo::igrf

#endif // IGRF_MODEL_HPP
