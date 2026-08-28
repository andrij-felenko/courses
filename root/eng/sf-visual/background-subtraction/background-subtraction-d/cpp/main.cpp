#include <cstdint>
#include <span>

#if defined(__ARM_FEATURE_DSP) && (__ARM_FEATURE_DSP == 1)
#include <arm_acle.h>

void subtract_simd_4px(std::span<const uint8_t, 4> frame,
                       std::span<const uint8_t, 4> bg,
                       std::span<uint8_t, 4> mask,
                       uint8_t threshold) noexcept {
    uint32_t f4;
    uint32_t b4;
    std::memcpy(&f4, frame.data(), sizeof(uint32_t));
    std::memcpy(&b4, bg.data(), sizeof(uint32_t));

    const uint32_t diff1 = __UQSUB8(f4, b4);
    const uint32_t diff2 = __UQSUB8(b4, f4);
    const uint32_t abs_diff = diff1 | diff2;

    const uint32_t thresh4 = (static_cast<uint32_t>(threshold) * 0x01010101u);
    __USUB8(abs_diff, thresh4);
    const uint32_t mask4 = __SEL(0xFFFFFFFFu, 0x00000000u);

    std::memcpy(mask.data(), &mask4, sizeof(uint32_t));
}
#else
void subtract_simd_4px(std::span<const uint8_t, 4> frame,
                       std::span<const uint8_t, 4> bg,
                       std::span<uint8_t, 4> mask,
                       uint8_t threshold) noexcept {
    for (size_t i = 0; i < 4; ++i) {
        const int16_t d = static_cast<int16_t>(frame[i]) - static_cast<int16_t>(bg[i]);
        mask[i] = (std::abs(d) > threshold) ? 255 : 0;
    }
}
#endif
