#include <vector>
#include <stdexcept>

struct Vec3 { double x{}, y{}, z{}; };

Vec3 center_of_mass(const std::vector<double>& mass,
                    const std::vector<Vec3>& pos) {
    double total = 0.0;
    Vec3 acc;                                   // {0, 0, 0}
    for (std::size_t i = 0; i < mass.size(); ++i) {
        total += mass[i];
        acc.x += mass[i] * pos[i].x;            // накопичуємо mᵢ·rᵢ
        acc.y += mass[i] * pos[i].y;
        acc.z += mass[i] * pos[i].z;
    }
    if (total == 0.0) throw std::invalid_argument("сумарна маса нульова");
    return { acc.x / total, acc.y / total, acc.z / total };
}
