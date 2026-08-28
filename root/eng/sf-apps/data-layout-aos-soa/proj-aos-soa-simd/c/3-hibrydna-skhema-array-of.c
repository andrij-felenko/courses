#include <stdlib.h>
#include <immintrin.h>

#define LANES 8

typedef struct {
    float x[LANES];
    float y[LANES];
    float z[LANES];
    float vx[LANES];
    float vy[LANES];
    float vz[LANES];
} ParticleTile; // 6 полів * 8 елементів * 4 байти = 192 байти (рівно 3 кеш-лінії)

void update_particles_aosoa_avx2(ParticleTile *restrict tiles, int num_tiles, float dt, float damping, float min_b, float max_b)
{
    __m256 v_damping = _mm256_set1_ps(damping);
    __m256 v_dt      = _mm256_set1_ps(dt);
    __m256 v_min     = _mm256_set1_ps(min_b);
    __m256 v_max     = _mm256_set1_ps(max_b);

    for (int t = 0; t < num_tiles; t++) {
        ParticleTile *tile = &tiles[t];

        // Векторне оновлення осі X
        __m256 vx = _mm256_loadu_ps(tile->vx);
        __m256 x  = _mm256_loadu_ps(tile->x);
        vx = _mm256_mul_ps(vx, v_damping);
        x  = _mm256_fmadd_ps(vx, v_dt, x);
        x  = _mm256_max_ps(v_min, _mm256_min_ps(v_max, x));
        _mm256_storeu_ps(tile->vx, vx);
        _mm256_storeu_ps(tile->x, x);

        // Векторне оновлення осі Y
        __m256 vy = _mm256_loadu_ps(tile->vy);
        __m256 y  = _mm256_loadu_ps(tile->y);
        vy = _mm256_mul_ps(vy, v_damping);
        y  = _mm256_fmadd_ps(vy, v_dt, y);
        y  = _mm256_max_ps(v_min, _mm256_min_ps(v_max, y));
        _mm256_storeu_ps(tile->vy, vy);
        _mm256_storeu_ps(tile->y, y);

        // Векторне оновлення осі Z
        __m256 vz = _mm256_loadu_ps(tile->vz);
        __m256 z  = _mm256_loadu_ps(tile->z);
        vz = _mm256_mul_ps(vz, v_damping);
        z  = _mm256_fmadd_ps(vz, v_dt, z);
        z  = _mm256_max_ps(v_min, _mm256_min_ps(v_max, z));
        _mm256_storeu_ps(tile->vz, vz);
        _mm256_storeu_ps(tile->z, z);
    }
}
