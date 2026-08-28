#include <vector>
#include <cstddef>

inline constexpr std::size_t SIMD_LANES = 8;

struct alignas(32) ParticleTile {
    float x[SIMD_LANES];
    float y[SIMD_LANES];
    float z[SIMD_LANES];
    float vx[SIMD_LANES];
    float vy[SIMD_LANES];
    float vz[SIMD_LANES];
};

std::vector<ParticleTile> tiles(1000000 / SIMD_LANES);
