#include <arm_neon.h>

/* Векторизований розрахунок IoU для 4 рамок одночасно на ARM NEON */
float32x4_t compute_iou_neon_4x(
    float32x4_t p_x1, float32x4_t p_y1, float32x4_t p_x2, float32x4_t p_y2,
    float32x4_t gt_x1, float32x4_t gt_y1, float32x4_t gt_x2, float32x4_t gt_y2
) {
    float32x4_t zero = vdupq_n_f32(0.0f);

    /* Координати прямокутника перетину */
    float32x4_t ix1 = vmaxq_f32(p_x1, gt_x1);
    float32x4_t iy1 = vmaxq_f32(p_y1, gt_y1);
    float32x4_t ix2 = vminq_f32(p_x2, gt_x2);
    float32x4_t iy2 = vminq_f32(p_y2, gt_y2);

    /* Ширина та висота перетину з обмеженням знизу нулем */
    float32x4_t iw = vmaxq_f32(zero, vsubq_f32(ix2, ix1));
    float32x4_t ih = vmaxq_f32(zero, vsubq_f32(iy2, iy1));
    float32x4_t inter_area = vmulq_f32(iw, ih);

    /* Площі окремих рамок */
    float32x4_t pw = vmaxq_f32(zero, vsubq_f32(p_x2, p_x1));
    float32x4_t ph = vmaxq_f32(zero, vsubq_f32(p_y2, p_y1));
    float32x4_t p_area = vmulq_f32(pw, ph);

    float32x4_t gtw = vmaxq_f32(zero, vsubq_f32(gt_x2, gt_x1));
    float32x4_t gth = vmaxq_f32(zero, vsubq_f32(gt_y2, gt_y1));
    float32x4_t gt_area = vmulq_f32(gtw, gth);

    /* Площа об'єднання за формулою включень-виключень */
    float32x4_t union_area = vsubq_f32(vaddq_f32(p_area, gt_area), inter_area);

    /* Векторне ділення площі перетину на площу об'єднання */
    return vdivq_f32(inter_area, union_area);
}
