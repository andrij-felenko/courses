#include <stdlib.h>
#include <immintrin.h>

typedef struct {
    float *x;
    float *y;
    float *z;
    float *vx;
    float *vy;
    float *vz;
} ParticlesSoA;

// Виділення вирівняної пам'яті під масиви SoA
ParticlesSoA allocate_soa(int n)
{
    ParticlesSoA p;
    size_t bytes = ((n + 7) & ~7) * sizeof(float); // Округлення до кратного 8
    p.x  = (float *)aligned_alloc(32, bytes);
    p.y  = (float *)aligned_alloc(32, bytes);
    p.z  = (float *)aligned_alloc(32, bytes);
    p.vx = (float *)aligned_alloc(32, bytes);
    p.vy = (float *)aligned_alloc(32, bytes);
    p.vz = (float *)aligned_alloc(32, bytes);
    return p;
}

void free_soa(ParticlesSoA *p)
{
    free(p->x);  free(p->y);  free(p->z);
    free(p->vx); free(p->vy); free(p->vz);
}

void update_particles_soa_avx2(ParticlesSoA *restrict p, int n, float dt, float damping, float min_b, float max_b)
{
    __m256 v_damping = _mm256_set1_ps(damping);
    __m256 v_dt      = _mm256_set1_ps(dt);
    __m256 v_min     = _mm256_set1_ps(min_b);
    __m256 v_max     = _mm256_set1_ps(max_b);

    int i = 0;
    // Обробка по 8 частинок за одну ітерацію (256-бітний AVX2)
    for (; i <= n - 8; i += 8) {
        // Оновлення X
        __m256 vx = _mm256_load_ps(&p->vx[i]);
        __m256 x  = _mm256_load_ps(&p->x[i]);
        vx = _mm256_mul_ps(vx, v_damping);
        x  = _mm256_fmadd_ps(vx, v_dt, x); // x + vx * dt за 1 такт
        x  = _mm256_max_ps(v_min, _mm256_min_ps(v_max, x)); // clamp
        _mm256_store_ps(&p->vx[i], vx);
        _mm256_store_ps(&p->x[i], x);

        // Оновлення Y
        __m256 vy = _mm256_load_ps(&p->vy[i]);
        __m256 y  = _mm256_load_ps(&p->y[i]);
        vy = _mm256_mul_ps(vy, v_damping);
        y  = _mm256_fmadd_ps(vy, v_dt, y);
        y  = _mm256_max_ps(v_min, _mm256_min_ps(v_max, y));
        _mm256_store_ps(&p->vy[i], vy);
        _mm256_store_ps(&p->y[i], y);

        // Оновлення Z
        __m256 vz = _mm256_load_ps(&p->vz[i]);
        __m256 z  = _mm256_load_ps(&p->z[i]);
        vz = _mm256_mul_ps(vz, v_damping);
        z  = _mm256_fmadd_ps(vz, v_dt, z);
        z  = _mm256_max_ps(v_min, _mm256_min_ps(v_max, z));
        _mm256_store_ps(&p->vz[i], vz);
        _mm256_store_ps(&p->z[i], z);
    }

    // Хвіст для елементів, що не кратні 8
    for (; i < n; i++) {
        float vx = p->vx[i] * damping;
        float vy = p->vy[i] * damping;
        float vz = p->vz[i] * damping;
        p->vx[i] = vx; p->vy[i] = vy; p->vz[i] = vz;

        float x = p->x[i] + vx * dt;
        float y = p->y[i] + vy * dt;
        float z = p->z[i] + vz * dt;
        p->x[i] = (x < min_b) ? min_b : (x > max_b ? max_b : x);
        p->y[i] = (y < min_b) ? min_b : (y > max_b ? max_b : y);
        p->z[i] = (z < min_b) ? min_b : (z > max_b ? max_b : z);
    }
}
