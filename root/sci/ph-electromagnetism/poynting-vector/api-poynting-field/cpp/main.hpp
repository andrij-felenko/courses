#ifndef POYNTING_SOLVER_HPP
#define POYNTING_SOLVER_HPP

#include <complex>
#include <span>
#include <expected>
#include <vector>
#include <array>
#include <cstddef>

namespace em::poynting {

using Complex = std::complex<double>;

struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Vector3D cross(const Vector3D& other) const noexcept {
        return Vector3D{
            y * other.z - z * other.y,
            z * other.x - x * other.z,
            x * other.y - y * other.x
        };
    }

    [[nodiscard]] constexpr double dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }
};

struct ComplexVector3D {
    Complex x{0.0, 0.0};
    Complex y{0.0, 0.0};
    Complex z{0.0, 0.0};

    [[nodiscard]] ComplexVector3D cross_conjugate(const ComplexVector3D& other) const noexcept {
        const Complex ox_conj = std::conj(other.x);
        const Complex oy_conj = std::conj(other.y);
        const Complex oz_conj = std::conj(other.z);

        return ComplexVector3D{
            y * oz_conj - z * oy_conj,
            z * ox_conj - x * oz_conj,
            x * oy_conj - y * ox_conj
        };
    }
};

struct SurfaceElement {
    Vector3D center;
    Vector3D normal;
    double area{0.0};
};

struct PoyntingSummary {
    double active_power_watts{0.0};
    double reactive_power_vars{0.0};
    double max_flux_density_w_m2{0.0};
};

enum class SolverErrorCode {
    InvalidSizeMismatch,
    NullPointerData,
    ZeroSurfaceArea
};

class PoyntingIntegrator {
public:
    [[nodiscard]] static constexpr Vector3D compute_instantaneous(
        const Vector3D& E, const Vector3D& H) noexcept {
        return E.cross(H);
    }

    [[nodiscard]] static ComplexVector3D compute_complex(
        const ComplexVector3D& E_c, const ComplexVector3D& H_c) noexcept {
        const auto flux = E_c.cross_conjugate(H_c);
        return ComplexVector3D{0.5 * flux.x, 0.5 * flux.y, 0.5 * flux.z};
    }

    [[nodiscard]] static std::expected<PoyntingSummary, SolverErrorCode> integrate_surface(
        std::span<const ComplexVector3D> e_fields,
        std::span<const ComplexVector3D> h_fields,
        std::span<const SurfaceElement> elements) noexcept
    {
        if (e_fields.size() != h_fields.size() || e_fields.size() != elements.size()) {
            return std::unexpected(SolverErrorCode::InvalidSizeMismatch);
        }
        if (elements.empty()) {
            return std::unexpected(SolverErrorCode::ZeroSurfaceArea);
        }

        PoyntingSummary summary{};
        for (std::size_t i = 0; i < elements.size(); ++i) {
            const auto S_c = compute_complex(e_fields[i], h_fields[i]);
            const Vector3D active_vec{S_c.x.real(), S_c.y.real(), S_c.z.real()};
            const Vector3D reactive_vec{S_c.x.imag(), S_c.y.imag(), S_c.z.imag()};

            const double active_flux = active_vec.dot(elements[i].normal) * elements[i].area;
            const double reactive_flux = reactive_vec.dot(elements[i].normal) * elements[i].area;

            summary.active_power_watts += active_flux;
            summary.reactive_power_vars += reactive_flux;

            const double flux_mag = std::sqrt(
                active_vec.x * active_vec.x +
                active_vec.y * active_vec.y +
                active_vec.z * active_vec.z
            );
            if (flux_mag > summary.max_flux_density_w_m2) {
                summary.max_flux_density_w_m2 = flux_mag;
            }
        }
        return summary;
    }
};

} // namespace em::poynting

#endif /* POYNTING_SOLVER_HPP */
