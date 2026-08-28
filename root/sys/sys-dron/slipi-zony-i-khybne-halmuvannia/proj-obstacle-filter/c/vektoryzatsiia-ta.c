#include <arm_neon.h>

/* Векторний розрахунок квадратів евклідових відстаней для 4 точок одночасно */
void calc_batch_distances_sq_neon(float px, float py, float pz,
                                   const float* target_x4, 
                                   const float* target_y4, 
                                   const float* target_z4,
                                   float* out_dist_sq4) {
    float32x4_t v_px = vdupq_n_f32(px);
    float32x4_t v_py = vdupq_n_f32(py);
    float32x4_t v_pz = vdupq_n_f32(pz);

    float32x4_t v_tx = vld1q_f32(target_x4);
    float32x4_t v_ty = vld1q_f32(target_y4);
    float32x4_t v_tz = vld1q_f32(target_z4);

    float32x4_t dx = vsubq_f32(v_px, v_tx);
    float32x4_t dy = vsubq_f32(v_py, v_ty);
    float32x4_t dz = vsubq_f32(v_pz, v_tz);

    float32x4_t dsq = vmulq_f32(dx, dx);
    dsq = vmlaq_f32(dsq, dy, dy);
    dsq = vmlaq_f32(dsq, dz, dz);

    vst1q_f32(out_dist_sq4, dsq);
}
