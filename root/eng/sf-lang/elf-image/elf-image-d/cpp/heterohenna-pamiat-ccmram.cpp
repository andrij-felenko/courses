#include <cstdint>

extern "C" {
    extern std::uint32_t _siccmram;
    extern std::uint32_t _sccmram;
    extern std::uint32_t _eccmram;
}

void copy_ccmram_section_cpp() noexcept {
    const std::uint32_t* src = &_siccmram;
    std::uint32_t* dst = &_sccmram;

    while (dst < &_eccmram) {
        *dst++ = *src++;
    }
}
