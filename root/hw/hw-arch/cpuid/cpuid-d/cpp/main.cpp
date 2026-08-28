#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <cstring>
#include <cpuid.h>

struct CpuInfo {
    std::string vendor;
    std::string brand;
    std::uint32_t max_basic_leaf{0};
    std::uint32_t max_extended_leaf{0};
    bool has_avx2{false};
    bool has_fma{false};
    bool is_hypervisor{false};
};

class CpuInspector {
public:
    static CpuInfo inspect() noexcept {
        CpuInfo info;
        std::uint32_t eax = 0, ebx = 0, ecx = 0, edx = 0;

        // 1. Листок 0: Максимальний базовий листок та Vendor String
        if (!__get_cpuid(0, &eax, &ebx, &ecx, &edx)) {
            return info;
        }
        info.max_basic_leaf = eax;

        std::array<char, 13> vendor_buf{};
        std::memcpy(vendor_buf.data() + 0, &ebx, 4);
        std::memcpy(vendor_buf.data() + 4, &edx, 4);
        std::memcpy(vendor_buf.data() + 8, &ecx, 4);
        info.vendor = vendor_buf.data();

        // 2. Листок 1: Базові можливості
        if (info.max_basic_leaf >= 1) {
            __cpuid(1, eax, ebx, ecx, edx);
            info.has_fma = (ecx & bit_FMA) != 0;
            info.is_hypervisor = (ecx & (1U << 31)) != 0;
        }

        // 3. Листок 7: Розширені прапорці (підлисток 0)
        if (info.max_basic_leaf >= 7) {
            __cpuid_count(7, 0, eax, ebx, ecx, edx);
            info.has_avx2 = (ebx & bit_AVX2) != 0;
        }

        // 4. Розширений простір: 0x80000000
        __cpuid(0x80000000, eax, ebx, ecx, edx);
        info.max_extended_leaf = eax;

        // 5. Листки 0x80000002..0x80000004: Brand String
        if (info.max_extended_leaf >= 0x80000004) {
            std::array<char, 49> brand_buf{};
            auto* words = reinterpret_cast<std::uint32_t*>(brand_buf.data());

            for (std::uint32_t leaf = 0x80000002; leaf <= 0x80000004; ++leaf) {
                __cpuid(leaf, eax, ebx, ecx, edx);
                *words++ = eax;
                *words++ = ebx;
                *words++ = ecx;
                *words++ = edx;
            }
            info.brand = brand_buf.data();
        }

        return info;
    }
};

int main() {
    const auto info = CpuInspector::inspect();

    std::cout << "Виробник процесора: " << info.vendor << "\n";
    std::cout << "Повна назва моделі: " << info.brand << "\n";
    std::cout << "Підтримка AVX2:     " << (info.has_avx2 ? "ТАК" : "НІ") << "\n";
    std::cout << "Віртуальна машина:  " << (info.is_hypervisor ? "ТАК" : "НІ") << "\n";

    return 0;
}
