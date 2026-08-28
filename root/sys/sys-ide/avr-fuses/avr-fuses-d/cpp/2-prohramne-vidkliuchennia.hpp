#include <cstdint>

struct AfioMapr {
    static constexpr std::uint32_t swj_cfg_mask    = 0x07000000U;
    static constexpr std::uint32_t swj_cfg_disable = 0x04000000U;
};

void release_swd_pins_to_gpio() noexcept {
    // Пряма безпечна модифікація регістрів конфігурації альтернативних функцій
    volatile std::uint32_t* const rcc_apb2enr = reinterpret_cast<std::uint32_t*>(0x40021018U);
    volatile std::uint32_t* const afio_mapr   = reinterpret_cast<std::uint32_t*>(0x40010004U);
    
    *rcc_apb2enr |= (1U << 0); // AFIOEN
    
    std::uint32_t val = *afio_mapr;
    val &= ~AfioMapr::swj_cfg_mask;
    val |= AfioMapr::swj_cfg_disable;
    *afio_mapr = val;
}
