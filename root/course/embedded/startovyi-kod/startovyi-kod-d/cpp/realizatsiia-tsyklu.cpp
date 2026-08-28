#include <cstdint>

/* Типізована реалізація ініціалізації пам'яті мовою C++ */
extern "C" {
    extern std::uint32_t _sidata;
    extern std::uint32_t _sdata;
    extern std::uint32_t _edata;
    extern std::uint32_t _sbss;
    extern std::uint32_t _ebss;
}

namespace mcu::startup {
    inline void init_memory_sections() noexcept {
        /* 1. Копіювання ініціалізованих змінних */
        const std::uint32_t* src = &_sidata;
        std::uint32_t* dst = &_sdata;
        while (dst < &_edata) {
            *dst++ = *src++;
        }

        /* 2. Обнулення неініціалізованих змінних */
        std::uint32_t* bss = &_sbss;
        while (bss < &_ebss) {
            *bss++ = 0;
        }
    }
}
