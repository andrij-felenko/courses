// Потокова обробка рядка у C++
void process_row(
    std::span<const uint8_t> binary_row,
    std::optional<std::span<int>> output_labels = std::nullopt
);

// Потокова обробка 3D зрізу у C++
void process_slice_3d(
    std::span<const uint8_t> binary_slice,
    std::optional<std::span<int>> output_labels = std::nullopt
);
