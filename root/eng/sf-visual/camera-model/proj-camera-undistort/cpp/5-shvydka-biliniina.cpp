namespace vision {

// Білінійна ректифікація кадру
void remap_bilinear_gray(std::span<const uint8_t> src_img,
                         int width, int height,
                         const ImageRemapper& remapper,
                         std::span<uint8_t> dst_img) {
    const auto map_x = remapper.map_x();
    const auto map_y = remapper.map_y();

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const int idx = y * width + x;
            const float sx = map_x[idx];
            const float sy = map_y[idx];

            const int x0 = static_cast<int>(std::floor(sx));
            const int y0 = static_cast<int>(std::floor(sy));
            const int x1 = x0 + 1;
            const int y1 = y0 + 1;

            if (x0 >= 0 && x1 < width && y0 >= 0 && y1 < height) {
                const float wx1 = sx - static_cast<float>(x0);
                const float wx0 = 1.0f - wx1;
                const float wy1 = sy - static_cast<float>(y0);
                const float wy0 = 1.0f - wy1;

                const float p00 = static_cast<float>(src_img[y0 * width + x0]);
                const float p01 = static_cast<float>(src_img[y0 * width + x1]);
                const float p10 = static_cast<float>(src_img[y1 * width + x0]);
                const float p11 = static_cast<float>(src_img[y1 * width + x1]);

                const float val = (p00 * wx0 + p01 * wx1) * wy0 +
                                  (p10 * wx0 + p11 * wx1) * wy1;

                dst_img[idx] = static_cast<uint8_t>(std::clamp(val + 0.5f, 0.0f, 255.0f));
            } else {
                dst_img[idx] = 0;
            }
        }
    }
}

} // namespace vision
