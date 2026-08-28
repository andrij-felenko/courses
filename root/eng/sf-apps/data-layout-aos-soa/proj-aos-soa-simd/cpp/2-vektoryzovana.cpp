#include <vector>
#include <memory>
#include <immintrin.h>
#include <algorithm>

// Алокатор із вирівнюванням під AVX2 (32 байти)
template <typename T, std::size_t Alignment = 32>
struct AlignedAllocator {
    using value_type = T;
    AlignedAllocator() noexcept = default;

    T* allocate(std::size_t n) {
        std::size_t bytes = n * sizeof(T);
        void* ptr = ::aligned_alloc(Alignment, (bytes + Alignment - 1) & ~(Alignment - 1));
        if (!ptr) throw std::bad_alloc();
        return static_cast<T*>(ptr);
    }

    void deallocate(T* p, std::size_t) noexcept {
        ::free(p);
    }
};

struct ParticlesSoA {
    std::vector<float, AlignedAllocator<float>> x, y, z;
    std::vector<float, AlignedAllocator<float>> vx, vy, vz;

    explicit ParticlesSoA(std::size_t n)
        : x(n), y(n), z(n), vx(n), vy(n), vz(n) {}

    [[nodiscard]] std::size_t size() const noexcept { return x.size(); }
};

void update_particles_soa_avx2(ParticlesSoA &p, float dt, float damping, float min_b, float max_b) noexcept
{
    const std::size_t n = p.size();
    const __m256 v_damping = _mm256_set1_ps(damping);
    const __m256 v_dt      = _mm256_set1_ps(dt);
    const __m256 v_min     = _mm256_set1_ps(min_b);
    const __m256 v_max     = _mm256_set1_ps(max_b);

    std::size_t i = 0;
    for (; i <= n - 8; i += 8) {
        // Оновлення компонентів через прямі векторні інструкції
        auto step_axis = [&](float* pos, float* vel) {
            __m256 v = _mm256_load_ps(vel + i);
            __m256 coord = _mm256_load_ps(pos + i);
            v = _mm256_mul_ps(v, v_damping);
            coord = _mm256_fmadd_ps(v, v_dt, coord);
            coord = _mm256_max_ps(v_min, _mm256_min_ps(v_max, coord));
            _mm256_store_ps(vel + i, v);
            _mm256_store_ps(pos + i, coord);
        };

        step_axis(p.x.data(), p.vx.data());
        step_axis(p.y.data(), p.vy.data());
        step_axis(p.z.data(), p.vz.data());
    }

    // Скалярний хвіст
    for (; i < n; ++i) {
        p.vx[i] *= damping;
        p.vy[i] *= damping;
        p.vz[i] *= damping;

        p.x[i] = std::clamp(p.x[i] + p.vx[i] * dt, min_b, max_b);
        p.y[i] = std::clamp(p.y[i] + p.vy[i] * dt, min_b, max_b);
        p.z[i] = std::clamp(p.z[i] + p.vz[i] * dt, min_b, max_b);
    }
}
