// Ректифікація 8-бітного одноканального (сірого) кадру
void remap_bilinear_gray(const uint8_t *src_img,
                         int width, int height,
                         const UndistortMap *map,
                         uint8_t *dst_img) {
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int idx = y * width + x;
            float sx = map->map_x[idx];
            float sy = map->map_y[idx];

            int x0 = (int)floorf(sx);
            int y0 = (int)floorf(sy);
            int x1 = x0 + 1;
            int y1 = y0 + 1;

            // Перевірка меж вхідного зображення
            if (x0 >= 0 && x1 < width && y0 >= 0 && y1 < height) {
                float wx1 = sx - (float)x0;
                float wx0 = 1.0f - wx1;
                float wy1 = sy - (float)y0;
                float wy0 = 1.0f - wy1;

                float p00 = (float)src_img[y0 * width + x0];
                float p01 = (float)src_img[y0 * width + x1];
                float p10 = (float)src_img[y1 * width + x0];
                float p11 = (float)src_img[y1 * width + x1];

                float val = (p00 * wx0 + p01 * wx1) * wy0 +
                            (p10 * wx0 + p11 * wx1) * wy1;

                dst_img[idx] = (uint8_t)(val + 0.5f);
            } else {
                dst_img[idx] = 0; // чорне тло за межами сенсора
            }
        }
    }
}
