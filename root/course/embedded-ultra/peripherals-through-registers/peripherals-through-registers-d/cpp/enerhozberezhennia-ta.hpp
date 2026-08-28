/* Увімкнення тактування порту GPIOA мовою C++ через типізовані константи */
namespace ClockControl {
    inline constexpr std::uintptr_t RccAhb1EnrAddress = 0x40023830UL;
    inline constexpr std::uint32_t GpioAEnableBit     = (1UL << 0);

    inline void enableGpioA() noexcept {
        auto* reg = reinterpret_cast<volatile std::uint32_t*>(RccAhb1EnrAddress);
        *reg |= GpioAEnableBit;
        (void)*reg; // Бар'єр синхронізації тактування
    }
}
