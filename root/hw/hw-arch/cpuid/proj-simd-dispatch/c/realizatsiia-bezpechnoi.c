#include <stdint.h>
#include <stdbool.h>
#include <cpuid.h>
#include <immintrin.h>

typedef struct {
    bool has_sse42;
    bool has_avx2;
    bool has_avx512f;
    bool has_avx512vl;
    bool has_fma;
    bool has_bmi2;
} CpuCapabilities;

static inline uint64_t read_xcr0(void) {
    uint32_t eax, edx;
    __asm__ __volatile__("xgetbv" : "=a"(eax), "=d"(edx) : "c"(0));
    return ((uint64_t)edx << 32) | eax;
}

CpuCapabilities detect_cpu_features(void) {
    CpuCapabilities caps = {false, false, false, false, false, false};
    uint32_t eax, ebx, ecx, edx;

    // Перевірка максимального доступного базового листка
    if (!__get_cpuid(0, &eax, &ebx, &ecx, &edx) || eax < 1) {
        return caps;
    }

    // Листок 1: базові можливості та OSXSAVE
    __cpuid(1, eax, ebx, ecx, edx);
    caps.has_sse42 = (ecx & bit_SSE4_2) != 0;
    caps.has_fma   = (ecx & bit_FMA) != 0;

    bool osxsave = (ecx & bit_OSXSAVE) != 0;
    bool ymm_supported = false;
    bool zmm_supported = false;

    if (osxsave) {
        uint64_t xcr0 = read_xcr0();
        // Біт 1 = SSE (XMM), біт 2 = AVX (YMM)
        ymm_supported = (xcr0 & 0x06) == 0x06;
        // Біти 5, 6, 7 = стан ZMM та Opmask для AVX-512
        zmm_supported = ymm_supported && ((xcr0 & 0xE0) == 0xE0);
    }

    // Листок 7 (підлисток 0): розширені прапорці
    if (eax >= 7) {
        __cpuid_count(7, 0, eax, ebx, ecx, edx);
        caps.has_bmi2 = (ebx & bit_BMI2) != 0;

        if (ymm_supported && (ebx & bit_AVX2)) {
            caps.has_avx2 = true;
        }
        if (zmm_supported) {
            caps.has_avx512f  = (ebx & bit_AVX512F) != 0;
            caps.has_avx512vl = (ebx & bit_AVX512VL) != 0;
        }
    }

    return caps;
}
