#include <cstdint>
#include <cpuid.h>
#include <immintrin.h>

struct CpuCapabilities {
    bool has_sse42{false};
    bool has_avx2{false};
    bool has_avx512f{false};
    bool has_avx512vl{false};
    bool has_fma{false};
    bool has_bmi2{false};
};

class CpuFeatureDetector {
public:
    static CpuCapabilities probe() noexcept {
        CpuCapabilities caps{};
        std::uint32_t eax = 0, ebx = 0, ecx = 0, edx = 0;

        if (!__get_cpuid(0, &eax, &ebx, &ecx, &edx) || eax < 1) {
            return caps;
        }

        __cpuid(1, eax, ebx, ecx, edx);
        caps.has_sse42 = (ecx & bit_SSE4_2) != 0;
        caps.has_fma   = (ecx & bit_FMA) != 0;

        const bool osxsave = (ecx & bit_OSXSAVE) != 0;
        bool ymm_supported = false;
        bool zmm_supported = false;

        if (osxsave) {
            const std::uint64_t xcr0 = read_xcr0();
            ymm_supported = (xcr0 & 0x06) == 0x06;
            zmm_supported = ymm_supported && ((xcr0 & 0xE0) == 0xE0);
        }

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

private:
    static std::uint64_t read_xcr0() noexcept {
        std::uint32_t eax = 0, edx = 0;
        __asm__ __volatile__("xgetbv" : "=a"(eax), "=d"(edx) : "c"(0));
        return (static_cast<std::uint64_t>(edx) << 32) | eax;
    }
};
