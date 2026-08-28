// Таблиця розраховується один раз: lut[i] = (uint16_t)(exp(-(i/255.0)^2 / 0.5) * 65536.0f)
static const uint16_t GAUSSIAN_DECAY_LUT[256] = {
    65536, 65535, 65534, 65530, 65525, 65518, 65509, 65498,
    65485, 65470, 65453, 65434, 65413, 65390, 65364, 65337,
    // ... 256 значень ...
    9065, 8932, 8801, 8671, 8543, 8416, 8291, 8167
};

static inline int32_t fast_gaussian_decay_q16(int32_t iou_scaled_255) {
    if (iou_scaled_255 <= 0) return 65536;
    if (iou_scaled_255 >= 255) return 8167;
    return (int32_t)GAUSSIAN_DECAY_LUT[iou_scaled_255];
}
