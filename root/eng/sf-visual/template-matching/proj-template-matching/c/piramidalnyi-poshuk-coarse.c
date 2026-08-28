void image_downsample_2x(const uint8_t *src, int src_w, int src_h, int src_stride,
                         uint8_t *dst, int dst_stride) {
    const int dst_w = src_w / 2;
    const int dst_h = src_h / 2;
    for (int y = 0; y < dst_h; ++y) {
        const uint8_t *r0 = src + (2 * y) * src_stride;
        const uint8_t *r1 = src + (2 * y + 1) * src_stride;
        uint8_t *out_row = dst + y * dst_stride;
        for (int x = 0; x < dst_w; ++x) {
            const int sum = (int)r0[2 * x] + (int)r0[2 * x + 1]
                          + (int)r1[2 * x] + (int)r1[2 * x + 1];
            out_row[x] = (uint8_t)((sum + 2) / 4);
        }
    }
}
