#include <arm_neon.h>
#include <array>

/* Векторизований розрахунок IoU для 4 рамок одночасно на ARM NEON (C++20) */
[[nodiscard]] inline float32x4_t compute_iou_neon_4x(
    float32x4_t p_x1, float32x4_t p_y1, float32x4_t p_x2, float32x4_t p_y2,
    float32x4_t gt_x1, float32x4_t gt_y1, float32x4_t gt_x2, float32x4_t gt_y2
) noexcept {
    const float32x4_t zero = vdupq_n_f32(0.0f);

    const float32x4_t ix1 = vmaxq_f32(p_x1, gt_x1);
    const float32x4_t iy1 = vmaxq_f32(p_y1, gt_y1);
    const float32x4_t ix2 = vminq_f32(p_x2, gt_x2);
    const float32x4_t iy2 = vminq_f32(p_y2, gt_y2);

    const float32x4_t iw = vmaxq_f32(zero, vsubq_f32(ix2, ix1));
    const float32x4_t ih = vmaxq_f32(zero, vsubq_f32(iy2, iy1));
    const float32x4_t inter_area = vmulq_f32(iw, ih);

    const float32x4_t pw = vmaxq_f32(zero, vsubq_f32(p_x2, p_x1));
    const float32x4_t ph = vmaxq_f32(zero, vsubq_f32(p_y2, p_y1));
    const float32x4_t p_area = vmulq_f32(pw, ph);

    const float32x4_t gtw = vmaxq_f32(zero, vsubq_f32(gt_x2, gt_x1));
    const float32x4_t gth = vmaxq_f32(zero, vsubq_f32(gt_y2, gt_y1));
    const float32x4_t gt_area = vmulq_f32(gtw, gth);

    const float32x4_t union_area = vsubq_f32(vaddq_f32(p_area, gt_area), inter_area);
    return vdivq_f32(inter_area, union_area);
}
