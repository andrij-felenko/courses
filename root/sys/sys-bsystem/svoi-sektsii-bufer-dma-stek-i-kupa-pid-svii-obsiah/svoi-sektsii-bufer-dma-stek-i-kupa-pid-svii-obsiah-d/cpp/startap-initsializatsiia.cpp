#include <cstdint>
#include <algorithm>
#include <span>

extern "C" {
    extern std::uint32_t _sidata;
    extern std::uint32_t _sdata;
    extern std::uint32_t _edata;
    extern std::uint32_t _sbss;
    extern std::uint32_t _ebss;

    void SystemInit() noexcept;
    void __libc_init_array() noexcept;
    int main();
}

namespace {

inline void copy_initialized_data() noexcept {
    const auto* src = &_sidata;
    auto* dst = &_sdata;
    const std::size_t count = static_cast<std::size_t>(&_edata - &_sdata);
    std::copy_n(src, count, dst);
}

inline void zero_uninitialized_bss() noexcept {
    auto* dst = &_sbss;
    const std::size_t count = static_cast<std::size_t>(&_ebss - &_sbss);
    std::fill_n(dst, count, 0U);
}

} // namespace

extern "C" void Reset_Handler() noexcept {
    copy_initialized_data();
    zero_uninitialized_bss();

    SystemInit();
    __libc_init_array();

    main();

    while (true) {
        // Пастка на випадок повернення
    }
}
