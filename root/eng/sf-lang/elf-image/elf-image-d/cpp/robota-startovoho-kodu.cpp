#include <cstdint>
#include <cstddef>
#include <algorithm>
#include <span>

extern "C" {
    extern std::uint32_t _sidata;
    extern std::uint32_t _sdata;
    extern std::uint32_t _edata;
    extern std::uint32_t _sbss;
    extern std::uint32_t _ebss;

    void SystemInit();
    int main();
    void __libc_init_array(); // Ініціалізація глобальних конструкторів C++
}

extern "C" void Reset_Handler_Cpp() noexcept {
    // 1. Копіювання .data з Flash LMA в SRAM VMA
    const std::uint32_t* src = &_sidata;
    std::uint32_t* dst_begin = &_sdata;
    std::uint32_t* dst_end = &_edata;

    while (dst_begin < dst_end) {
        *dst_begin++ = *src++;
    }

    // 2. Очищення секції .bss в SRAM VMA
    std::uint32_t* bss_begin = &_sbss;
    std::uint32_t* bss_end = &_ebss;

    while (bss_begin < bss_end) {
        *bss_begin++ = 0U;
    }

    // 3. Апаратна ініціалізація генераторів тактової частоти
    SystemInit();

    // 4. Виклик конструкторів глобальних та статичних об'єктів C++ (.init_array)
    __libc_init_array();

    // 5. Виклик точки входу програми
    main();

    // Запобігання виходу в невизначений стан
    while (true) {
        #if defined(__arm__) || defined(__thumb__)
        asm volatile("wfi"); // Очікування переривання (Wait For Interrupt)
        #endif
    }
}
