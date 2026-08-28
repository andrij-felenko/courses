/* Копіювання секції .ramfunc у C++ */
#include <cstdint>

extern "C" {
    extern uint32_t _si_ramfunc;
    extern uint32_t _sramfunc;
    extern uint32_t _eramfunc;
}

namespace mcu::startup {

inline void copy_ramfunc() noexcept {
    const uint32_t* src = &_si_ramfunc;
    uint32_t* dst = &_sramfunc;
    while (dst < &_eramfunc) {
        *dst++ = *src++;
    }
    asm volatile("dsb 0xF" ::: "memory");
    asm volatile("isb 0xF" ::: "memory");
}

} // namespace mcu::startup
