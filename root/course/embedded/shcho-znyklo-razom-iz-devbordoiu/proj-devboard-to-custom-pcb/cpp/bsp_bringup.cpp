// bsp_bringup.cpp — Реалізація мовою C++
#include "bsp_bringup.hpp"
#include <span>

namespace bsp {

namespace {
    // Типізоване зв'язування з апаратними регістрами Cortex-M
    inline volatile uint32_t& reg_rcc_cr     = *reinterpret_cast<volatile uint32_t*>(0x40023800UL);
    inline volatile uint32_t& reg_rcc_cfgr   = *reinterpret_cast<volatile uint32_t*>(0x40023808UL);
    inline volatile uint32_t& reg_rcc_csr    = *reinterpret_cast<volatile uint32_t*>(0x40023874UL);

    inline volatile uint32_t& reg_gpioa_mod  = *reinterpret_cast<volatile uint32_t*>(0x40020000UL);
    inline volatile uint32_t& reg_gpiob_mod  = *reinterpret_cast<volatile uint32_t*>(0x40020400UL);
    inline volatile uint32_t& reg_gpioc_mod  = *reinterpret_cast<volatile uint32_t*>(0x40020800UL);

    inline volatile uint32_t& reg_dhcsr      = *reinterpret_cast<volatile uint32_t*>(0xE000EDF0UL);
    inline volatile uint8_t&  reg_itm_port0  = *reinterpret_cast<volatile uint8_t*>(0xE0000000UL);
    inline volatile uint32_t& reg_itm_ter    = *reinterpret_cast<volatile uint32_t*>(0xE0000E00UL);

    constexpr uint32_t hsi_on_bit    = 1UL << 0;
    constexpr uint32_t hsi_rdy_bit   = 1UL << 1;
    constexpr uint32_t hse_on_bit    = 1UL << 16;
    constexpr uint32_t hse_rdy_bit   = 1UL << 17;

    constexpr uint32_t csr_rmvf_bit  = 1UL << 24;
    constexpr uint32_t csr_bor_bit   = 1UL << 25;
    constexpr uint32_t csr_por_bit   = 1UL << 27;
    constexpr uint32_t csr_sft_bit   = 1UL << 28;
    constexpr uint32_t csr_iwdg_bit  = 1UL << 29;

    constexpr uint32_t debug_en_bit  = 1UL << 0;
}

std::expected<ClockSourceStatus, ClockSourceStatus> 
BringupManager::init_clock_safe(uint32_t hse_timeout_cycles) noexcept {
    // 1. Активація внутрішнього генератора HSI
    reg_rcc_cr |= hsi_on_bit;
    while (!(reg_rcc_cr & hsi_rdy_bit)) {
        // Очікування стабілізації HSI
    }

    // 2. Спроба запуску зовнішнього кварцового генератора HSE
    reg_rcc_cr |= hse_on_bit;
    uint32_t countdown = hse_timeout_cycles;

    while (!(reg_rcc_cr & hse_rdy_bit) && (countdown > 0)) {
        --countdown;
    }

    if (countdown == 0) {
        // Аварійне вимкнення контуру HSE після таймауту
        reg_rcc_cr &= ~hse_on_bit;
        reg_rcc_cfgr &= ~0x03UL; // SW = HSI
        return std::unexpected(ClockSourceStatus::HsiFallback);
    }

    // 3. Перемикання системної шини на HSE
    reg_rcc_cfgr = (reg_rcc_cfgr & ~0x03UL) | 0x01UL;
    while ((reg_rcc_cfgr & 0x0CUL) != 0x04UL) {
        // Очікування готовності мультиплексора
    }

    return ClockSourceStatus::HseCrystal;
}

void BringupManager::park_unused_pins() noexcept {
    // Зберігаємо виводи SWD (PA13, PA14) при глобальному переводі в аналоговий стан
    auto moder_a = reg_gpioa_mod;
    moder_a |= 0x03FFFFFFUL;
    moder_a &= ~(0x3UL << (13 * 2));
    moder_a |=  (0x2UL << (13 * 2)); // PA13 -> AF
    moder_a &= ~(0x3UL << (14 * 2));
    moder_a |=  (0x2UL << (14 * 2)); // PA14 -> AF
    reg_gpioa_mod = moder_a;

    reg_gpiob_mod = 0xFFFFFFFFUL; // Analog mode для порту B
    reg_gpioc_mod = 0xFFFFFFFFUL; // Analog mode для порту C
}

void BringupManager::log(std::string_view message) noexcept {
    if ((reg_dhcsr & debug_en_bit) && (reg_itm_ter & 0x01UL)) {
        for (const char ch : message) {
            reg_itm_port0 = static_cast<uint8_t>(ch);
        }
    }
}

HardwareHealth BringupManager::check_health() noexcept {
    HardwareHealth health{};
    const uint32_t csr = reg_rcc_csr;

    if (csr & csr_bor_bit) {
        health.reset_reason = ResetCause::Brownout;
    } else if (csr & csr_por_bit) {
        health.reset_reason = ResetCause::PowerOn;
    } else if (csr & csr_iwdg_bit) {
        health.reset_reason = ResetCause::Watchdog;
    } else if (csr & csr_sft_bit) {
        health.reset_reason = ResetCause::Software;
    } else {
        health.reset_reason = ResetCause::Unknown;
    }

    reg_rcc_csr |= csr_rmvf_bit;

    health.debugger_connected = (reg_dhcsr & debug_en_bit) != 0;
    health.clock_status = (reg_rcc_cr & hse_rdy_bit) 
                          ? ClockSourceStatus::HseCrystal 
                          : ClockSourceStatus::HsiFallback;

    health.core_frequency_hz = (health.clock_status == ClockSourceStatus::HseCrystal) 
                               ? 25'000'000UL 
                               : 16'000'000UL;

    return health;
}

} // namespace bsp
