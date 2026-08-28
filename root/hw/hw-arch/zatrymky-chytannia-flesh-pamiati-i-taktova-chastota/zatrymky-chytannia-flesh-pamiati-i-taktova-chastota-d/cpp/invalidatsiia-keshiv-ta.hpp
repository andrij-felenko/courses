/* Безпечна інвалідація кешу інструкцій та даних у C++ */
namespace mcu::flash {

inline void cache_flush() noexcept {
    auto& acr = *reinterpret_cast<volatile uint32_t*>(0x40023C00U);
    constexpr uint32_t IcenBit  = 1U << 9;
    constexpr uint32_t DcenBit  = 1U << 10;
    constexpr uint32_t IcrstBit = 1U << 11;
    constexpr uint32_t DcrstBit = 1U << 12;

    /* Вимикаємо кеші перед скиданням тегів */
    acr &= ~(IcenBit | DcenBit);
    acr |= (IcrstBit | DcrstBit);
    acr &= ~(IcrstBit | DcrstBit);
    acr |= (IcenBit | DcenBit);
}

} // namespace mcu::flash
