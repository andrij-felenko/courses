#include <vector>
#include <span>
#include <cstdint>

std::vector<uint8_t> downsample_2x(std::span<const uint8_t> src, int src_w, int src_h, int src_stride) {
    const int dst_w = src_w / 2;
    const int dst_h = src_h / 2;
    std::vector<uint8_t> dst(dst_w * dst_h);

    for (int y = 0; y < dst_h; ++y) {
        const uint8_t *r0 = src.data() + (2 * y) * src_stride;
        const uint8_t *r1 = src.data() + (2 * y + 1) * src_stride;
        uint8_t *out_row = dst.data() + y * dst_w;
        for (int x = 0; x < dst_w; ++x) {
            const int sum = static_cast<int>(r0[2 * x]) + static_cast<int>(r0[2 * x + 1])
                          + static_cast<int>(r1[2 * x]) + static_cast<int>(r1[2 * x + 1]);
            out_row[x] = static_cast<uint8_t>((sum + 2) / 4);
        }
    }
    return dst;
}
