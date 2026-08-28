#include <stdint.h>
#include <stdbool.h>

#define MDIO_REG_BMSR           0x01
#define MDIO_BMSR_LINK_STATUS   (1U << 2)
#define MDIO_BMSR_AN_COMPLETE   (1U << 5)

// Апаратне читання 16-бітного регістру через контролер MAC/MDIO
extern uint16_t hal_mdio_read(uint8_t phy_addr, uint8_t reg_addr);

bool mdio_read_phy_link_state(uint8_t phy_addr) {
    // Перше зчитування: очищення збереженого прапорця Latch-Low
    (void)hal_mdio_read(phy_addr, MDIO_REG_BMSR);

    // Друге зчитування: отримання реального миттєвого стану лінії
    uint16_t bmsr = hal_mdio_read(phy_addr, MDIO_REG_BMSR);

    bool link_up = (bmsr & MDIO_BMSR_LINK_STATUS) != 0;
    bool autoneg_done = (bmsr & MDIO_BMSR_AN_COMPLETE) != 0;

    return link_up && autoneg_done;
}
