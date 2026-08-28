// Константна таблиця у ROM на C++20
constexpr std::array<uint16_t, 256> GAUSSIAN_DECAY_LUT = {
    65536, 65535, 65534, 65530, 65525, 65518, 65509, 65498,
    65485, 65470, 65453, 65434, 65413, 65390, 65364, 65337,
    // ... 256 значень ...
    9065, 8932, 8801, 8671, 8543, 8416, 8291, 8167
};

[[nodiscard]] constexpr int32_t fast_gaussian_decay_q16(int32_t iou_scaled_255) noexcept {
    if (iou_scaled_255 <= 0) return 65536;
    if (iou_scaled_255 >= 255) return 8167;
    return static_cast<int32_t>(GAUSSIAN_DECAY_LUT[static_cast<size_t>(iou_scaled_255)]);
}
