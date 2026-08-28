// Завантаження координат чотирьох рамок (C++20 std::span)
int32x4_t vx1 = vld1q_s32(boxes_x1.data() + i);
int32x4_t vy1 = vld1q_s32(boxes_y1.data() + i);
int32x4_t vx2 = vld1q_s32(boxes_x2.data() + i);
int32x4_t vy2 = vld1q_s32(boxes_y2.data() + i);

// Паралельний розрахунок кутів перетину з лідером M
int32x4_t inter_x1 = vmaxq_s32(vx1, vdupq_n_s32(m_x1));
int32x4_t inter_y1 = vmaxq_s32(vy1, vdupq_n_s32(m_y1));
int32x4_t inter_x2 = vminq_s32(vx2, vdupq_n_s32(m_x2));
int32x4_t inter_y2 = vminq_s32(vy2, vdupq_n_s32(m_y2));

// Розрахунок ширини та висоти з обмеженням 0
int32x4_t zero = vdupq_n_s32(0);
int32x4_t inter_w = vmaxq_s32(zero, vsubq_s32(inter_x2, inter_x1));
int32x4_t inter_h = vmaxq_s32(zero, vsubq_s32(inter_y2, inter_y1));
int32x4_t inter_area = vmulq_s32(inter_w, inter_h);
