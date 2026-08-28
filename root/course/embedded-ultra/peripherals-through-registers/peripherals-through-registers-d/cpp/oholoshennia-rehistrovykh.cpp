/* Оголошення структури регістрів GPIO мовою C++ */
struct GpioHardwareLayout {
    volatile std::uint32_t MODER;    // +0x00
    volatile std::uint32_t OTYPER;   // +0x04
    volatile std::uint32_t OSPEEDR;  // +0x08
    volatile std::uint32_t PUPDR;    // +0x0C
    volatile std::uint32_t IDR;      // +0x10
    volatile std::uint32_t ODR;      // +0x14
    volatile std::uint32_t BSRR;     // +0x18
    volatile std::uint32_t LCKR;     // +0x1C
    volatile std::uint32_t AFR[2];   // +0x20
};

inline constexpr std::uintptr_t GpioABase = 0x40020000UL;
inline auto* const GpioAInstance = reinterpret_cast<GpioHardwareLayout*>(GpioABase);
