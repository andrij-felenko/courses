#include <arm_neon.h>
#include <span>

void update_particles_neon_soa(std::span<float> x, std::span<float> y, std::span<float> z,
                               std::span<float> vx, std::span<float> vy, std::span<float> vz,
                               float dt, float damping, float min_b, float max_b) noexcept
{
    const float32x4_t v_damping = vdupq_n_f32(damping);
    const float32x4_t v_dt      = vdupq_n_f32(dt);
    const float32x4_t v_min     = vdupq_n_f32(min_b);
    const float32x4_t v_max     = vdupq_n_f32(max_b);
    const std::size_t n         = x.size();

    for (std::size_t i = 0; i <= n - 4; i += 4) {
        auto step_dim = [&](float* pos_ptr, float* vel_ptr) {
            float32x4_t v = vld1q_f32(vel_ptr + i);
            float32x4_t coord = vld1q_f32(pos_ptr + i);
            v = vmulq_f32(v, v_damping);
            coord = vfmaq_f32(coord, v, v_dt);
            coord = vmaxq_f32(v_min, vminq_f32(v_max, coord));
            vst1q_f32(vel_ptr + i, v);
            vst1q_f32(pos_ptr + i, coord);
        };

        step_dim(x.data(), vx.data());
        step_dim(y.data(), vy.data());
        step_dim(z.data(), vz.data());
    }
}
