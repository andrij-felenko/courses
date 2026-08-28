#include <array>
#include <cmath>
#include <concepts>
#include <expected>
#include <numbers>
#include <optional>
#include <span>
#include <algorithm>

namespace gnss {

constexpr double SpeedOfLight   = 299792458.0;      // м/с
constexpr double EarthRotRate   = 7.2921151467e-5;  // рад/с (WGS-84)
constexpr double ConvergenceTol = 1e-4;             // 0.1 мм
constexpr size_t MaxIterations  = 10;

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr double norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
};

struct SatelliteObservation {
    Vector3D positionEcef; // ECEF координати супутника (м)
    double pseudorange;    // Сира псевдодальність (м)
    double clockOffset;    // Поправка годинника супутника (с)
    double elevation;      // Кут піднесення (рад)
};

struct Solution {
    Vector3D positionEcef;
    double clockBiasMeters{0.0};
    double gdop{0.0}, pdop{0.0}, hdop{0.0}, vdop{0.0}, tdop{0.0};
    size_t iterations{0};
};

enum class SolverError {
    InsufficientSatellites,
    DegenerateGeometry,
    Divergence
};

using Matrix4x4 = std::array<std::array<double, 4>, 4>;
using Vector4   = std::array<double, 4>;

[[nodiscard]] constexpr std::optional<Matrix4x4> invert(const Matrix4x4& a) noexcept {
    std::array<std::array<double, 8>, 4> aug{};
    for (size_t i = 0; i < 4; ++i) {
        for (size_t j = 0; j < 4; ++j) {
            aug[i][j] = a[i][j];
            aug[i][j + 4] = (i == j) ? 1.0 : 0.0;
        }
    }

    for (size_t col = 0; col < 4; ++col) {
        size_t pivot = col;
        double maxVal = std::abs(aug[col][col]);
        for (size_t row = col + 1; row < 4; ++row) {
            if (const double v = std::abs(aug[row][col]); v > maxVal) {
                maxVal = v;
                pivot = row;
            }
        }
        if (maxVal < 1e-15) return std::nullopt;

        if (pivot != col) {
            std::swap(aug[col], aug[pivot]);
        }

        const double scale = aug[col][col];
        for (size_t k = 0; k < 8; ++k) aug[col][k] /= scale;

        for (size_t row = 0; row < 4; ++row) {
            if (row != col) {
                const double factor = aug[row][col];
                for (size_t k = 0; k < 8; ++k) {
                    aug[row][k] -= factor * aug[col][k];
                }
            }
        }
    }

    Matrix4x4 inv{};
    for (size_t i = 0; i < 4; ++i)
        for (size_t j = 0; j < 4; ++j)
            inv[i][j] = aug[i][j + 4];
    return inv;
}

class LeastSquaresSolver {
public:
    [[nodiscard]] static std::expected<Solution, SolverError> solve(
        std::span<const SatelliteObservation> satellites) noexcept {
        if (satellites.size() < 4) {
            return std::unexpected(SolverError::InsufficientSatellites);
        }

        Vector4 state{0.0, 0.0, 0.0, 0.0}; // [X, Y, Z, c*dt]

        for (size_t iter = 0; iter < MaxIterations; ++iter) {
            Matrix4x4 normalMatrix{};
            Vector4   rhs{};

            for (const auto& sat : satellites) {
                // Врахування обертання Землі (Sagnac effect)
                const double approxDist = Vector3D{
                    sat.positionEcef.x - state[0],
                    sat.positionEcef.y - state[1],
                    sat.positionEcef.z - state[2]
                }.norm();

                const double tau = approxDist / SpeedOfLight;
                const double alpha = EarthRotRate * tau;

                const double xSatRot =  std::cos(alpha) * sat.positionEcef.x + std::sin(alpha) * sat.positionEcef.y;
                const double ySatRot = -std::sin(alpha) * sat.positionEcef.x + std::cos(alpha) * sat.positionEcef.y;
                const double zSatRot = sat.positionEcef.z;

                const double rx = state[0] - xSatRot;
                const double ry = state[1] - ySatRot;
                const double rz = state[2] - zSatRot;
                const double geomDist = std::max(1.0, std::sqrt(rx * rx + ry * ry + rz * rz));

                const Vector4 u{ rx / geomDist, ry / geomDist, rz / geomDist, 1.0 };
                const double corrPr = sat.pseudorange + SpeedOfLight * sat.clockOffset;
                const double expectedPr = geomDist + state[3];
                const double deltaRho = corrPr - expectedPr;

                const double sinEl = std::sin(std::max(sat.elevation, 0.0872));
                const double weight = sinEl * sinEl;

                for (size_t r = 0; r < 4; ++r) {
                    for (size_t c = 0; c < 4; ++c) {
                        normalMatrix[r][c] += u[r] * u[c] * weight;
                    }
                    rhs[r] += u[r] * weight * deltaRho;
                }
            }

            const auto invN = invert(normalMatrix);
            if (!invN) {
                return std::unexpected(SolverError::DegenerateGeometry);
            }

            Vector4 deltaX{};
            for (size_t r = 0; r < 4; ++r) {
                for (size_t c = 0; c < 4; ++c) {
                    deltaX[r] += (*invN)[r][c] * rhs[c];
                }
                state[r] += deltaX[r];
            }

            const double stepNorm = Vector3D{deltaX[0], deltaX[1], deltaX[2]}.norm();
            if (stepNorm < ConvergenceTol) {
                Solution sol{};
                sol.positionEcef = { state[0], state[1], state[2] };
                sol.clockBiasMeters = state[3];
                sol.iterations = iter + 1;
                calculateDop(*invN, sol.positionEcef, sol);
                return sol;
            }
        }

        return std::unexpected(SolverError::Divergence);
    }

private:
    static void calculateDop(const Matrix4x4& invN, const Vector3D& pos, Solution& sol) noexcept {
        const double p = std::sqrt(pos.x * pos.x + pos.y * pos.y);
        const double lat = std::atan2(pos.z, p);
        const double lon = std::atan2(pos.y, pos.x);

        const double sLat = std::sin(lat), cLat = std::cos(lat);
        const double sLon = std::sin(lon), cLon = std::cos(lon);

        const std::array<std::array<double, 3>, 3> rot = {{
            { -sLon,          cLon,         0.0  },
            { -sLat * cLon, -sLat * sLon, cLat  },
            {  cLat * cLon,  cLat * sLon, sLat  }
        }};

        std::array<std::array<double, 3>, 3> temp{};
        for (size_t i = 0; i < 3; ++i)
            for (size_t j = 0; j < 3; ++j)
                for (size_t k = 0; k < 3; ++k)
                    temp[i][j] += rot[i][k] * invN[k][j];

        std::array<std::array<double, 3>, 3> qEnu{};
        for (size_t i = 0; i < 3; ++i)
            for (size_t j = 0; j < 3; ++j)
                for (size_t k = 0; k < 3; ++k)
                    qEnu[i][j] += temp[i][k] * rot[j][k];

        const double qE = qEnu[0][0];
        const double qN = qEnu[1][1];
        const double qU = qEnu[2][2];
        const double qT = invN[3][3];

        sol.hdop = std::sqrt(std::max(0.0, qE + qN));
        sol.vdop = std::sqrt(std::max(0.0, qU));
        sol.pdop = std::sqrt(std::max(0.0, qE + qN + qU));
        sol.tdop = std::sqrt(std::max(0.0, qT));
        sol.gdop = std::sqrt(std::max(0.0, qE + qN + qU + qT));
    }
};

} // namespace gnss
