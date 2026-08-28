#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <cpuid.h>
#include <immintrin.h>

#define ALIGNMENT_XSAVE 64

/* Структура 64-байтного заголовка кадру XSAVE */
typedef struct {
    uint64_t xstate_bv;      /* Бітова маска збережених компонентів */
    uint64_t xcomp_bv;      /* Бітова маска стисненого формату */
    uint64_t reserved[6];   /* 48 байтів резерву (мусять бути суворо нулями) */
} __attribute__((packed)) xsave_header_t;

/* Отримання регістра XCR0 за допомогою асемблерної інструкції xgetbv */
static inline uint64_t read_xcr0(void) {
    uint32_t eax, edx;
    __asm__ volatile("xgetbv" : "=a"(eax), "=d"(edx) : "c"(0));
    return ((uint64_t)edx << 32) | eax;
}

/* Безпечна обгортка над інструкцією XSAVE64 з бар'єром пам'яті */
static inline void xsave64_state(void *buffer, uint64_t mask) {
    uint32_t eax = (uint32_t)mask;
    uint32_t edx = (uint32_t)(mask >> 32);
    __asm__ volatile(
        "xsave64 %0"
        : "+m"(*(uint8_t *)buffer)
        : "a"(eax), "d"(edx)
        : "memory"
    );
}

/* Безпечна обгортка над інструкцією XRSTOR64 */
static inline void xrstor64_state(const void *buffer, uint64_t mask) {
    uint32_t eax = (uint32_t)mask;
    uint32_t edx = (uint32_t)(mask >> 32);
    __asm__ volatile(
        "xrstor64 %0"
        :
        : "m"(*(const uint8_t *)buffer), "a"(eax), "d"(edx)
        : "memory"
    );
}

/* Перевірка підтримки XSAVE операційною системою та визначення розміру буфера */
bool detect_xsave_support(size_t *required_size, uint64_t *enabled_features) {
    uint32_t eax, ebx, ecx, edx;

    /* 1. Перевірка CPUID Leaf 1 на наявність біта OSXSAVE (ECX біт 27) */
    __cpuid(1, eax, ebx, ecx, edx);
    if (!(ecx & (1u << 27))) {
        fprintf(stderr, "Помилка: ОС або процесор не підтримують XSAVE (OSXSAVE=0)\\n");
        return false;
    }

    /* 2. Запит розміру буфера через CPUID Leaf 0xD, Subleaf 0 */
    __cpuid_count(0xD, 0, eax, ebx, ecx, edx);
    *required_size = (size_t)ebx; /* EBX повертає розмір для активного XCR0 */

    /* 3. Зчитування активної бітової маски компонентів з XCR0 */
    *enabled_features = read_xcr0();
    return true;
}

int main(void) {
    size_t buffer_size = 0;
    uint64_t xcr0_mask = 0;

    if (!detect_xsave_support(&buffer_size, &xcr0_mask)) {
        return EXIT_FAILURE;
    }

    printf("Розширений стан XSAVE успішно виявлено:\\n");
    printf("  Необхідний розмір буфера : %zu байтів\\n", buffer_size);
    printf("  Активна маска регістра XCR0: 0x%016llX\\n", (unsigned long long)xcr0_mask);

    /* Виділення динамічної пам'яті з обов'язковим вирівнюванням на 64 байти */
    uint8_t *xsave_area = (uint8_t *)aligned_alloc(ALIGNMENT_XSAVE, buffer_size);
    if (!xsave_area) {
        perror("Помилка виділення вирівняної пам'яті");
        return EXIT_FAILURE;
    }

    /* Гарантоване занулення буфера, включаючи зарезервовану зону заголовка */
    memset(xsave_area, 0, buffer_size);

    /* Виконання збереження активного контексту процесора */
    xsave64_state(xsave_area, xcr0_mask);

    /* Заголовок XSAVE розташований рівно за зсувом 512 байтів */
    xsave_header_t *hdr = (xsave_header_t *)(xsave_area + 512);
    printf("\\nАналіз збереженого кадру XSAVE:\\n");
    printf("  Маска XSTATE_BV (активні секції): 0x%016llX\\n", (unsigned long long)hdr->xstate_bv);
    printf("  Маска XCOMP_BV (формат кадру)   : 0x%016llX\\n", (unsigned long long)hdr->xcomp_bv);

    if (hdr->xstate_bv & (1ull << 0)) printf("  [+] x87 FPU стан збережено у Legacy області\\n");
    if (hdr->xstate_bv & (1ull << 1)) printf("  [+] SSE стан (XMM0-XMM15) зафіксовано\\n");
    if (hdr->xstate_bv & (1ull << 2)) printf("  [+] AVX стан (верхня половина YMM) збережено\\n");
    if (hdr->xstate_bv & (1ull << 5)) printf("  [+] AVX-512 Opmask (k0-k7) збережено\\n");
    if (hdr->xstate_bv & (1ull << 6)) printf("  [+] AVX-512 ZMM_Hi256 (верхня чверть ZMM0-15) збережено\\n");
    if (hdr->xstate_bv & (1ull << 7)) printf("  [+] AVX-512 Hi16_ZMM (повні регістри ZMM16-31) збережено\\n");
    if (hdr->xstate_bv & (1ull << 9)) printf("  [+] PKRU стан ключів захисту пам'яті збережено\\n");
    if (hdr->xstate_bv & (1ull << 17)) printf("  [+] AMX конфігурація плиток (TILECFG) активна\\n");
    if (hdr->xstate_bv & (1ull << 18)) printf("  [+] AMX дані матричних плиток (TILEDATA, 8 КБ) збережено\\n");

    free(xsave_area);
    return EXIT_SUCCESS;
}
