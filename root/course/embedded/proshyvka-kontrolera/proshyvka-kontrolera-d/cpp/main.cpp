#include <cstdint>
#include <concepts>

namespace fc::bootloader {

inline constexpr std::uintptr_t sram_lower = 0x20000000U;
inline constexpr std::uintptr_t sram_upper = 0x20080000U;

struct VectorHeader {
    std::uint32_t msp;
    std::uint32_t reset_handler;
};

[[nodiscard]] constexpr bool is_sram_address(std::uint32_t addr) noexcept {
    return (addr >= sram_lower) && (addr <= sram_upper);
}

[[nodiscard]] constexpr bool is_thumb_entry(std::uint32_t entry_addr) noexcept {
    return (entry_addr & 0x01U) == 0x01U;
}

[[noreturn]] void launch_firmware(std::uintptr_t target_flash_address) noexcept {
    const auto* const header = reinterpret_cast<const VectorHeader*>(target_flash_address);

    if (!is_sram_address(header->msp) || !is_thumb_entry(header->reset_handler)) {
        while (true) {
            // Пастка цілісності: зупинка перед хибним стрибком
        }
    }

    // 1. Заборона переривань
    asm volatile("cpsid i" ::: "memory");

    // 2. Деініціалізація SysTick
    auto* const systick_ctrl = reinterpret_cast<volatile std::uint32_t*>(0xE000E010U);
    auto* const systick_val  = reinterpret_cast<volatile std::uint32_t*>(0xE000E018U);
    *systick_ctrl = 0U;
    *systick_val  = 0U;

    // 3. Скидання NVIC
    auto* const icer = reinterpret_cast<volatile std::uint32_t*>(0xE000E180U);
    auto* const icpr = reinterpret_cast<volatile std::uint32_t*>(0xE000E280U);
    for (std::size_t i = 0; i < 8; ++i) {
        icer[i] = 0xFFFFFFFFU;
        icpr[i] = 0xFFFFFFFFU;
    }

    // 4. Релокація VTOR
    auto* const vtor = reinterpret_cast<volatile std::uint32_t*>(0xE000ED08U);
    *vtor = static_cast<std::uint32_t>(target_flash_address);

    asm volatile("dsb\n\tisb" ::: "memory");
    asm volatile("msr msp, %0" :: "r"(header->msp) : "memory");

    using EntryFn = void (*)() noexcept;
    auto entry_point = reinterpret_cast<EntryFn>(header->reset_handler);
    entry_point();

    while (true) {}
}

} // namespace fc::bootloader
