#include <arm_neon.h>
#include <array>
#include <span>

struct SimdPointBatch {
    std::array<float, 4> x{};
    std::array<float, 4> y{};
    std::array<float, 4> z{};

    [[nodiscard]] std::array<float, 4> compute_distances_sq(const Point3D& query) const noexcept {
        const float32x4_t v_px = vdupq_n_f32(query.x);
        const float32x4_t v_py = vdupq_n_f32(query.y);
        const float32x4_t v_pz = vdupq_n_f32(query.z);

        const float32x4_t v_tx = vld1q_f32(x.data());
        const float32x4_t v_ty = vld1q_f32(y.data());
        const float32x4_t v_tz = vld1q_f32(z.data());

        const float32x4_t dx = vsubq_f32(v_px, v_tx);
        const float32x4_t dy = vsubq_f32(v_py, v_ty);
        const float32x4_t dz = vsubq_f32(v_pz, v_tz);

        float32x4_t dsq = vmulq_f32(dx, dx);
        dsq = vmlaq_f32(dsq, dy, dy);
        dsq = vmlaq_f32(dsq, dz, dz);

        std::array<float, 4> result{};
        vst1q_f32(result.data(), dsq);
        return result;
    }
};
