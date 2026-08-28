// Приклад сканування шини MDC/MDIO та виявлення активних PHY на C++20
#include <cstdint>
#include <optional>
#include <span>

extern auto mdio_read_c22(uint8_t phy_addr, uint8_t reg_addr) noexcept -> std::optional<uint16_t>;

[[nodiscard]] auto scan_mdio_bus() noexcept -> uint32_t {
    uint32_t active_phys = 0;
    for (uint8_t addr = 0; addr < 32; ++addr) {
        const auto phy_id1 = mdio_read_c22(addr, 0x02);
        if (phy_id1.has_value() && *phy_id1 != 0xFFFFU && *phy_id1 != 0x0000U) {
            active_phys |= (1U << addr);
        }
    }
    return active_phys; // Бітова маска знайдених трансиверів
}
