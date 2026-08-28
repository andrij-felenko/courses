#if defined(__ARM_NEON)
#include <arm_neon.h>
#include <span>
#include <cstdint>

namespace embedded_ml::simd {

[[nodiscard]] inline float compute_sq_euclidean_neon(
    std::span<const float> a,
    std::span<const float> b
) noexcept {
    float32x4_t vsum = vdupq_n_f32(0.0f);
    const std::size_t dim = a.size();
    for (std::size_t d = 0; d < dim; d += 4) {
        float32x4_t va = vld1q_f32(&a[d]);
        float32x4_t vb = vld1q_f32(&b[d]);
        float32x4_t vdiff = vsubq_f32(va, vb);
        vsum = vmlaq_f32(vsum, vdiff, vdiff);
    }
    return vaddvq_f32(vsum);
}

} // namespace embedded_ml::simd
#endif
