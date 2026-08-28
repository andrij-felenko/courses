#include <vector>
#include <span>
#include <immintrin.h>

inline constexpr std::size_t SIMD_LANES = 8;

struct alignas(32) ParticleTile {
    float x[SIMD_LANES];
    float y[SIMD_LANES];
    float z[SIMD_LANES];
    float vx[SIMD_LANES];
    float vy[SIMD_LANES];
    float vz[SIMD_LANES];
};

void update_particles_aosoa_avx2(std::span<ParticleTile> tiles, float dt, float damping, float min_b, float max_b) noexcept
{
    const __m256 v_damping = _mm256_set1_ps(damping);
    const __m256 v_dt      = _mm256_set1_ps(dt);
    const __m256 v_min     = _mm256_set1_ps(min_b);
    const __m256 v_max     = _mm256_set1_ps(max_b);

    for (auto &tile : tiles) {
        auto step_axis = [&](float (&pos)[SIMD_LANES], float (&vel)[SIMD_LANES]) {
            __m256 v = _mm256_load_ps(vel);
            __m256 coord = _mm256_load_ps(pos);
            v = _mm256_mul_ps(v, v_damping);
            coord = _mm256_fmadd_ps(v, v_dt, coord);
            coord = _mm256_max_ps(v_min, _mm256_min_ps(v_max, coord));
            _mm256_store_ps(vel, v);
            _mm256_store_ps(pos, coord);
        };

        step_axis(tile.x, tile.vx);
        step_axis(tile.y, tile.vy);
        step_axis(tile.z, tile.vz);
    }
}
