/* Приклад сканування шини MDC/MDIO та виявлення активних PHY на мові C */
#include <stdint.h>
#include <stdbool.h>

extern bool mdio_read_c22(uint8_t phy_addr, uint8_t reg_addr, uint16_t *val);

uint32_t scan_mdio_bus(void) {
    uint32_t active_phys = 0;
    for (uint8_t addr = 0; addr < 32; ++addr) {
        uint16_t phy_id1 = 0;
        /* Читаємо Регістр 2 (PHYID1) */
        if (mdio_read_c22(addr, 0x02, &phy_id1)) {
            /* Відкрита шина повертає 0xFFFF, коротке замикання — 0x0000 */
            if (phy_id1 != 0xFFFFU && phy_id1 != 0x0000U) {
                active_phys |= (1U << addr);
            }
        }
    }
    return active_phys; // Бітова маска знайдених трансиверів
}
