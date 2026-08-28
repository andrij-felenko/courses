#include <arm_neon.h>
#include <cstdint>
#include <cstddef>
#include <span>

// Ідіоматична C++20 NEON векторизація для ARM64
void vec_div10_neon(std::span<const std::uint32_t> src, std::span<std::uint32_t> dst) noexcept {
    const std::size_t count = src.size();
    std::size_t i = 0;
    const uint32x2_t mult = vdup_n_u32(0xCCCCCCCDU);
    
    for (; i + 3 < count; i += 4) {
        const uint32x4_t v = vld1q_u32(src.data() + i);
        
        const uint64x2_t prod_low  = vmull_u32(vget_low_u32(v), mult);
        const uint64x2_t prod_high = vmull_high_u32(v, mult);
        
        const uint32x2_t q_low  = vmovn_u64(vshrq_n_u64(prod_low, 35));
        const uint32x2_t q_high = vmovn_u64(vshrq_n_u64(prod_high, 35));
        
        vst1q_u32(dst.data() + i, vcombine_u32(q_low, q_high));
    }
    
    for (; i < count; ++i) {
        dst[i] = src[i] / 10U;
    }
}
