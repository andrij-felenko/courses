#include <arm_neon.h>
#include <stdint.h>
#include <stddef.h>

// Векторне ділення 4 елементів uint32_t на 10 для ARM64 NEON
void vec_div10_neon(const uint32_t* src, uint32_t* dst, size_t count) {
    size_t i = 0;
    uint32x2_t mult = vdup_n_u32(0xCCCCCCCDU);
    
    for (; i + 3 < count; i += 4) {
        uint32x4_t v = vld1q_u32(src + i);
        
        // Множимо нижню пару (0, 1) та верхню пару (2, 3)
        uint64x2_t prod_low  = vmull_u32(vget_low_u32(v), mult);
        uint64x2_t prod_high = vmull_high_u32(v, mult);
        
        // Зсуваємо обидва 64-бітні вектори на 35 бітів праворуч
        uint32x2_t q_low  = vmovn_u64(vshrq_n_u64(prod_low, 35));
        uint32x2_t q_high = vmovn_u64(vshrq_n_u64(prod_high, 35));
        
        // Об'єднуємо два 32-бітні вектори розміром 2 у єдиний 32-бітний вектор розміром 4
        uint32x4_t res = vcombine_u32(q_low, q_high);
        vst1q_u32(dst + i, res);
    }
    
    for (; i < count; i++) {
        dst[i] = src[i] / 10U;
    }
}
