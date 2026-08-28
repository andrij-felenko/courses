#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <expected>
#include <string_view>
#include <span>
#include <iomanip>

namespace geodesy {

inline constexpr double ArcsecToRad = 4.8481368110953599e-6;

enum class Convention {
    PositionVector,  // EPSG: 9606 (IERS, ISO 19111, активний поворот)
    CoordinateFrame  // EPSG: 9607 (Bursa-Wolf, пасивний поворот)
};

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vec3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
};

struct Helmert7 {
    double tx{0.0};    // м
    double ty{0.0};    // м
    double tz{0.0};    // м
    double rx{0.0};    // кутові секунди
    double ry{0.0};    // кутові секунди
    double rz{0.0};    // кутові секунди
    double s_ppm{0.0}; // ppm (10^-6)
    Convention convention{Convention::PositionVector};

    [[nodiscard]] Vec3 forward(const Vec3& p) const noexcept {
        const double sign = (convention == Convention::CoordinateFrame) ? -1.0 : 1.0;
        const double rot_x = rx * ArcsecToRad * sign;
        const double rot_y = ry * ArcsecToRad * sign;
        const double rot_z = rz * ArcsecToRad * sign;
        const double scale = 1.0 + s_ppm * 1.0e-6;

        return {
            tx + scale * ( p.x - rot_z * p.y + rot_y * p.z),
            ty + scale * ( rot_z * p.x + p.y - rot_x * p.z),
            tz + scale * (-rot_y * p.x + rot_x * p.y + p.z)
        };
    }

    [[nodiscard]] Vec3 inverse(const Vec3& p) const noexcept {
        const Vec3 d = p - Vec3{tx, ty, tz};
        const double sign = (convention == Convention::CoordinateFrame) ? -1.0 : 1.0;
        const double rot_x = rx * ArcsecToRad * sign;
        const double rot_y = ry * ArcsecToRad * sign;
        const double rot_z = rz * ArcsecToRad * sign;
        const double inv_scale = 1.0 / (1.0 + s_ppm * 1.0e-6);

        return {
            inv_scale * ( d.x + rot_z * d.y - rot_y * d.z),
            inv_scale * (-rot_z * d.x + d.y + rot_x * d.z),
            inv_scale * ( rot_y * d.x - rot_x * d.y + d.z)
        };
    }
};

struct Helmert10 {
    Helmert7 h7;
    Vec3 centroid; // (X0, Y0, Z0), м

    [[nodiscard]] Vec3 forward(const Vec3& p) const noexcept {
        const Vec3 p_rel = p - centroid;
        const double sign = (h7.convention == Convention::CoordinateFrame) ? -1.0 : 1.0;
        const double rot_x = h7.rx * ArcsecToRad * sign;
        const double rot_y = h7.ry * ArcsecToRad * sign;
        const double rot_z = h7.rz * ArcsecToRad * sign;
        const double scale = 1.0 + h7.s_ppm * 1.0e-6;

        const Vec3 rot_p{
            scale * ( p_rel.x - rot_z * p_rel.y + rot_y * p_rel.z),
            scale * ( rot_z * p_rel.x + p_rel.y - rot_x * p_rel.z),
            scale * (-rot_y * p_rel.x + rot_x * p_rel.y + p_rel.z)
        };

        return centroid + Vec3{h7.tx, h7.ty, h7.tz} + rot_p;
    }
};

struct Helmert14 {
    Helmert7 base;
    double dtx{0.0};      // м/рік
    double dty{0.0};      // м/рік
    double dtz{0.0};      // м/рік
    double drx{0.0};      // кутові секунди/рік
    double dry{0.0};      // кутові секунди/рік
    double drz{0.0};      // кутові секунди/рік
    double ds_ppm{0.0};   // ppm/рік
    double epoch_t0{2000.0};

    [[nodiscard]] Helmert7 at_epoch(double epoch_t) const noexcept {
        const double dt = epoch_t - epoch_t0;
        return {
            .tx = base.tx + dtx * dt,
            .ty = base.ty + dty * dt,
            .tz = base.tz + dtz * dt,
            .rx = base.rx + drx * dt,
            .ry = base.ry + dry * dt,
            .rz = base.rz + drz * dt,
            .s_ppm = base.s_ppm + ds_ppm * dt,
            .convention = base.convention
        };
    }
};

// Оцінка 7 параметрів МНК
[[nodiscard]] std::expected<Helmert7, std::string_view> estimate_helmert7(
    std::span<const Vec3> src,
    std::span<const Vec3> tgt,
    Convention convention = Convention::PositionVector) noexcept
{
    if (src.size() != tgt.size() || src.size() < 3) {
        return std::unexpected("Потрібно щонайменше 3 спільні точки");
    }

    std::array<std::array<double, 7>, 7> N{};
    std::array<double, 7> U{};

    for (size_t i = 0; i < src.size(); ++i) {
        const auto [x, y, z] = src[i];
        const auto [tx_val, ty_val, tz_val] = tgt[i];

        const double lx = tx_val - x;
        const double ly = ty_val - y;
        const double lz = tz_val - z;

        std::array<std::array<double, 7>, 3> A{{
            { 1.0, 0.0, 0.0,  0.0 * ArcsecToRad,  z * ArcsecToRad, -y * ArcsecToRad, x * 1.0e-6 },
            { 0.0, 1.0, 0.0, -z * ArcsecToRad,  0.0 * ArcsecToRad,  x * ArcsecToRad, y * 1.0e-6 },
            { 0.0, 0.0, 1.0,  y * ArcsecToRad, -x * ArcsecToRad,  0.0 * ArcsecToRad, z * 1.0e-6 }
        }};

        if (convention == Convention::CoordinateFrame) {
            for (auto& row : A) {
                row[3] = -row[3];
                row[4] = -row[4];
                row[5] = -row[5];
            }
        }

        const std::array<double, 3> L{lx, ly, lz};

        for (size_t j = 0; j < 7; ++j) {
            for (size_t k = 0; k < 7; ++k) {
                for (size_t r = 0; r < 3; ++r) {
                    N[j][k] += A[r][j] * A[r][k];
                }
            }
            for (size_t r = 0; r < 3; ++r) {
                U[j] += A[r][j] * L[r];
            }
        }
    }

    // Розв'язання системи N * x = U методом виключення Гауса
    std::array<std::array<double, 8>, 7> Aug{};
    for (size_t i = 0; i < 7; ++i) {
        for (size_t j = 0; j < 7; ++j) Aug[i][j] = N[i][j];
        Aug[i][7] = U[i];
    }

    for (size_t col = 0; col < 7; ++col) {
        size_t pivot = col;
        double max_val = std::abs(Aug[col][col]);
        for (size_t r = col + 1; r < 7; ++r) {
            if (std::abs(Aug[r][col]) > max_val) {
                max_val = std::abs(Aug[r][col]);
                pivot = r;
            }
        }
        if (max_val < 1e-15) return std::unexpected("Матриця нормальних рівнянь вироджена");

        if (pivot != col) std::swap(Aug[col], Aug[pivot]);

        for (size_t r = col + 1; r < 7; ++r) {
            const double factor = Aug[r][col] / Aug[col][col];
            for (size_t k = col; k < 8; ++k) {
                Aug[r][k] -= factor * Aug[col][k];
            }
        }
    }

    std::array<double, 7> sol{};
    for (int r = 6; r >= 0; --r) {
        double sum = Aug[r][7];
        for (size_t k = r + 1; k < 7; ++k) {
            sum -= Aug[r][k] * sol[k];
        }
        sol[r] = sum / Aug[r][r];
    }

    return Helmert7{
        .tx = sol[0],
        .ty = sol[1],
        .tz = sol[2],
        .rx = sol[3],
        .ry = sol[4],
        .rz = sol[5],
        .s_ppm = sol[6],
        .convention = convention
    };
}

} // namespace geodesy

int main() {
    using namespace geodesy;

    const Helmert7 ed50_to_wgs84{
        .tx = -89.5,
        .ty = -93.8,
        .tz = -123.1,
        .rx = 0.0,
        .ry = 0.0,
        .rz = -0.156,
        .s_ppm = -1.2,
        .convention = Convention::PositionVector
    };

    const Vec3 pt_ed50{3978280.0, -100410.0, 4968390.0};
    const Vec3 pt_wgs84 = ed50_to_wgs84.forward(pt_ed50);
    const Vec3 pt_back  = ed50_to_wgs84.inverse(pt_wgs84);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Пряме перетворення ED50 -> WGS84:\n"
              << "  X: " << pt_ed50.x << " -> " << pt_wgs84.x << " м\n"
              << "  Y: " << pt_ed50.y << " -> " << pt_wgs84.y << " м\n"
              << "  Z: " << pt_ed50.z << " -> " << pt_wgs84.z << " м\n\n";

    std::cout << std::setprecision(6);
    std::cout << "Нев'язка зворотного перетворення:\n"
              << "  dX: " << (pt_back.x - pt_ed50.x) * 1000.0 << " мм, "
              << "dY: " << (pt_back.y - pt_ed50.y) * 1000.0 << " мм, "
              << "dZ: " << (pt_back.z - pt_ed50.z) * 1000.0 << " мм\n";

    return 0;
}
