#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <cpuid.h>

typedef struct {
    char vendor[13];
    char brand[49];
    uint32_t max_basic_leaf;
    uint32_t max_extended_leaf;
    bool has_avx2;
    bool has_fma;
    bool is_hypervisor;
} CpuInfo;

void query_cpu_info(CpuInfo* info) {
    memset(info, 0, sizeof(CpuInfo));
    uint32_t eax, ebx, ecx, edx;

    // 1. Листок 0: Максимальний базовий листок та Vendor String
    if (!__get_cpuid(0, &eax, &ebx, &ecx, &edx)) {
        return;
    }
    info->max_basic_leaf = eax;

    // Збираємо 12 байтів назви виробника: EBX -> EDX -> ECX
    memcpy(info->vendor + 0, &ebx, 4);
    memcpy(info->vendor + 4, &edx, 4);
    memcpy(info->vendor + 8, &ecx, 4);
    info->vendor[12] = '\0';

    // 2. Листок 1: Базові можливості
    if (info->max_basic_leaf >= 1) {
        __cpuid(1, eax, ebx, ecx, edx);
        info->has_fma = (ecx & bit_FMA) != 0;
        info->is_hypervisor = (ecx & (1U << 31)) != 0;
    }

    // 3. Листок 7: Розширені прапорці (підлисток 0)
    if (info->max_basic_leaf >= 7) {
        __cpuid_count(7, 0, eax, ebx, ecx, edx);
        info->has_avx2 = (ebx & bit_AVX2) != 0;
    }

    // 4. Розширений простір: 0x80000000
    __cpuid(0x80000000, eax, ebx, ecx, edx);
    info->max_extended_leaf = eax;

    // 5. Листки 0x80000002..0x80000004: Brand String
    if (info->max_extended_leaf >= 0x80000004) {
        uint32_t* brand_words = (uint32_t*)info->brand;
        for (uint32_t leaf = 0x80000002; leaf <= 0x80000004; ++leaf) {
            __cpuid(leaf, eax, ebx, ecx, edx);
            *brand_words++ = eax;
            *brand_words++ = ebx;
            *brand_words++ = ecx;
            *brand_words++ = edx;
        }
        info->brand[48] = '\0';
    }
}

int main(void) {
    CpuInfo info;
    query_cpu_info(&info);

    printf("Виробник процесора: %s\n", info.vendor);
    printf("Повна назва моделі: %s\n", info.brand);
    printf("Підтримка AVX2:     %s\n", info.has_avx2 ? "ТАК" : "НІ");
    printf("Віртуальна машина:  %s\n", info.is_hypervisor ? "ТАК" : "НІ");

    return 0;
}
