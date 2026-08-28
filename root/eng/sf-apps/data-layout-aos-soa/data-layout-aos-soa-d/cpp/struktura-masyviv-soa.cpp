#include <vector>
#include <cstdint>

struct ParticlesSoA {
    std::vector<float> x, y, z;
    std::vector<float> vx, vy, vz;
    std::vector<float> mass;
    std::vector<float> radius;
    std::vector<int32_t> id;
    std::vector<int32_t> flags;

    explicit ParticlesSoA(std::size_t n)
        : x(n), y(n), z(n), vx(n), vy(n), vz(n),
          mass(n), radius(n), id(n), flags(n) {}
};
