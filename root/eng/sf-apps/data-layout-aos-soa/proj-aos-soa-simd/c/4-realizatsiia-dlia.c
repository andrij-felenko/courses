#include <arm_neon.h>

void update_particles_neon_soa(float *restrict x, float *restrict y, float *restrict z,
                               float *restrict vx, float *restrict vy, float *restrict vz,
                               int n, float dt, float damping, float min_b, float max_b)
{
    float32x4_t v_damping = vdupq_n_f32(damping);
    float32x4_t v_dt      = vdupq_n_f32(dt);
    float32x4_t v_min     = vdupq_n_f32(min_b);
    float32x4_t v_max     = vdupq_n_f32(max_b);

    for (int i = 0; i <= n - 4; i += 4) {
        // Завантаження 4 елементів X
        float32x4_t v_vx = vld1q_f32(&vx[i]);
        float32x4_t v_x  = vld1q_f32(&x[i]);
        v_vx = vmulq_f32(v_vx, v_damping);
        v_x  = vfmaq_f32(v_x, v_vx, v_dt); // Fused Multiply-Accumulate
        v_x  = vmaxq_f32(v_min, vminq_f32(v_max, v_x));
        vst1q_f32(&vx[i], v_vx);
        vst1q_f32(&x[i], v_x);

        // Аналогічно для Y та Z...
    }
}
