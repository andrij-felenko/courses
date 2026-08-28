#if defined(__ARM_NEON)
#include <arm_neon.h>
static float compute_sq_euclidean_neon(const float *a, const float *b, uint32_t dim) {
    float32x4_t vsum = vdupq_n_f32(0.0f);
    for (uint32_t d = 0; d < dim; d += 4) {
        float32x4_t va = vld1q_f32(&a[d]);
        float32x4_t vb = vld1q_f32(&b[d]);
        float32x4_t vdiff = vsubq_f32(va, vb);
        vsum = vmlaq_f32(vsum, vdiff, vdiff);
    }
    return vaddvq_f32(vsum);
}
#endif
