namespace bsp::debug {

struct GpioRegisters {
    volatile std::uint32_t moder;
    volatile std::uint32_t otyper;
    volatile std::uint32_t ospeedr;
    volatile std::uint32_t pupdr;
    volatile std::uint32_t idr;
    volatile std::uint32_t odr;
    volatile std::uint32_t bsrr;
    volatile std::uint32_t lckr;
    volatile std::uint32_t afr[2];
};

inline auto& gpioa = *reinterpret_cast<GpioRegisters*>(0x40020000UL);
inline auto& rcc_ahb1enr = *reinterpret_cast<volatile std::uint32_t*>(0x40023830UL);

inline void init_mco1_pll_div4() noexcept {
    // 1. Тактування GPIOA
    rcc_ahb1enr |= (1UL << 0);

    // 2. Режим AF (10b) на піні PA8
    gpioa.moder &= ~(3UL << 16);
    gpioa.moder |=  (2UL << 16);

    // 3. AF0 (MCO1)
    gpioa.afr[1] &= ~(0xFUL << 0);

    // 4. High Speed (11b)
    gpioa.ospeedr |= (3UL << 16);

    // 5. Джерело PLL, дільник /4
    bsp::clock::rcc.cfgr &= ~((3UL << 21) | (7UL << 24));
    bsp::clock::rcc.cfgr |=  ((3UL << 21) | (6UL << 24));
}

} // namespace bsp::debug
