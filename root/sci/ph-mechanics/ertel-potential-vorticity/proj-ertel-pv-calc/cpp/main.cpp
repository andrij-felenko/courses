#include <vector>
#include <span>
#include <expected>
#include <cmath>
#include <cstddef>

constexpr double PVU_SCALE = 1e6;

struct Grid3D {
    int nx{0}, ny{0}, nz{0};
    double dx{1000.0}, dy{1000.0}, dz{100.0};
    double f0{1e-4};
};

struct FlowFields {
    std::span<const double> u;
    std::span<const double> v;
    std::span<const double> w;
    std::span<const double> theta;
    std::span<const double> rho;
};

enum class PVError {
    InvalidGridDimensions,
    BufferSpanMismatch,
    ZeroDensityEncountered
};

class ErtelPVCalculator {
public:
    static std::expected<std::vector<double>, PVError> compute(
        const Grid3D& grid, const FlowFields& fields) 
    {
        if (grid.nx < 3 || grid.ny < 3 || grid.nz < 3) {
            return std::unexpected(PVError::InvalidGridDimensions);
        }

        const size_t total_size = static_cast<size_t>(grid.nx) * grid.ny * grid.nz;
        if (fields.u.size() != total_size || fields.v.size() != total_size ||
            fields.w.size() != total_size || fields.theta.size() != total_size ||
            fields.rho.size() != total_size) 
        {
            return std::unexpected(PVError::BufferSpanMismatch);
        }

        std::vector<double> pv_out(total_size, 0.0);

        const auto idx = [ny = grid.ny, nz = grid.nz](int i, int j, int k) constexpr -> size_t {
            return (static_cast<size_t>(i) * ny + j) * nz + k;
        };

        const double dx2 = 2.0 * grid.dx;
        const double dy2 = 2.0 * grid.dy;
        const double dz2 = 2.0 * grid.dz;

        for (int i = 1; i < grid.nx - 1; ++i) {
            for (int j = 1; j < grid.ny - 1; ++j) {
                for (int k = 1; k < grid.nz - 1; ++k) {
                    const size_t c  = idx(i, j, k);
                    const size_t ip = idx(i + 1, j, k);
                    const size_t im = idx(i - 1, j, k);
                    const size_t jp = idx(i, j + 1, k);
                    const size_t jm = idx(i, j - 1, k);
                    const size_t kp = idx(i, j, k + 1);
                    const size_t km = idx(i, j, k - 1);

                    // Складові відносної вихореності
                    const double rel_wx = (fields.w[jp] - fields.w[jm]) / dy2 - (fields.v[kp] - fields.v[km]) / dz2;
                    const double rel_wy = (fields.u[kp] - fields.u[km]) / dz2 - (fields.w[ip] - fields.w[im]) / dx2;
                    const double rel_wz = (fields.v[ip] - fields.v[im]) / dx2 - (fields.u[jp] - fields.u[jm]) / dy2;

                    // Складові градієнта стратифікації
                    const double dth_dx = (fields.theta[ip] - fields.theta[im]) / dx2;
                    const double dth_dy = (fields.theta[jp] - fields.theta[jm]) / dy2;
                    const double dth_dz = (fields.theta[kp] - fields.theta[km]) / dz2;

                    // Абсолютна вихореність
                    const double abs_wx = rel_wx;
                    const double abs_wy = rel_wy;
                    const double abs_wz = rel_wz + grid.f0;

                    const double dot = abs_wx * dth_dx + abs_wy * dth_dy + abs_wz * dth_dz;
                    const double density = fields.rho[c];

                    if (std::abs(density) < 1e-9) {
                        return std::unexpected(PVError::ZeroDensityEncountered);
                    }

                    pv_out[c] = (dot / density) * PVU_SCALE;
                }
            }
        }

        return pv_out;
    }
};
