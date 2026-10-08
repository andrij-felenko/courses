#include <vector>
#include <array>

struct Vector3f {
    float x;
    float y;
    float z;
};

// Формування нормальної системи МНК (DᵀD · v = Dᵀy) для апроксимації 3D-еліпсоїда
void build_least_squares_system(const std::vector<Vector3f>& points,
                                std::array<std::array<double, 9>, 9>& dtd,
                                std::array<double, 9>& dty) {
    for (auto& row : dtd) {
        row.fill(0.0);
    }
    dty.fill(0.0);

    for (const auto& pt : points) {
        const double x = pt.x;
        const double y = pt.y;
        const double z = pt.z;

        const std::array<double, 9> row = {
            x * x,
            y * y,
            z * z,
            2.0 * x * y,
            2.0 * x * z,
            2.0 * y * z,
            2.0 * x,
            2.0 * y,
            2.0 * z
        };

        for (size_t i = 0; i < 9; ++i) {
            dty[i] += row[i];
            for (size_t j = 0; j < 9; ++j) {
                dtd[i][j] += row[i] * row[j];
            }
        }
    }
}
