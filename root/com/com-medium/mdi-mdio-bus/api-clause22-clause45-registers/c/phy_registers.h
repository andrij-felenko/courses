/* phy_registers.h - Визначення стандартних констант IEEE 802.3 Clause 22 та 45 */
#ifndef PHY_REGISTERS_H
#define PHY_REGISTERS_H

#include <stdint.h>
#include <stdbool.h>

/* Базові регістри Clause 22 */
#define PHY_REG_BMCR          0x00U  /* Basic Mode Control Register */
#define PHY_REG_BMSR          0x01U  /* Basic Mode Status Register */
#define PHY_REG_PHYID1        0x02U  /* PHY Identifier 1 (OUI bits 3..18) */
#define PHY_REG_PHYID2        0x03U  /* PHY Identifier 2 (OUI bits 19..24, Model, Rev) */
#define PHY_REG_ANAR          0x04U  /* Auto-Negotiation Advertisement Register */
#define PHY_REG_ANLPAR        0x05U  /* Auto-Negotiation Link Partner Ability */
#define PHY_REG_ANER          0x06U  /* Auto-Negotiation Expansion Register */
#define PHY_REG_1000CR        0x09U  /* 1000BASE-T Control Register */
#define PHY_REG_1000SR        0x0AU  /* 1000BASE-T Status Register */
#define PHY_REG_MMD_CTRL      0x0DU  /* MMD Access Control Register */
#define PHY_REG_MMD_DATA      0x0EU  /* MMD Access Address/Data Register */
#define PHY_REG_EXT_STATUS    0x0FU  /* Extended Status Register */

/* Біти BMCR (Регістр 0) */
#define BMCR_RESET            (1U << 15)
#define BMCR_LOOPBACK         (1U << 14)
#define BMCR_SPEED_100        (1U << 13)
#define BMCR_AUTONEG_EN       (1U << 12)
#define BMCR_POWER_DOWN       (1U << 11)
#define BMCR_ISOLATE          (1U << 10)
#define BMCR_RESTART_AN       (1U << 9)
#define BMCR_FULL_DUPLEX      (1U << 8)
#define BMCR_COLLISION_TEST   (1U << 7)
#define BMCR_SPEED_1000       (1U << 6)

/* Біти BMSR (Регістр 1) */
#define BMSR_100BASE_T4       (1U << 15)
#define BMSR_100_TX_FD        (1U << 14)
#define BMSR_100_TX_HD        (1U << 13)
#define BMSR_10_T_FD          (1U << 12)
#define BMSR_10_T_HD          (1U << 11)
#define BMSR_PREAMBLE_SUPPR   (1U << 6)
#define BMSR_AN_COMPLETE      (1U << 5)
#define BMSR_REMOTE_FAULT     (1U << 4)
#define BMSR_AN_ABILITY       (1U << 3)
#define BMSR_LINK_STATUS      (1U << 2)
#define BMSR_JABBER_DETECT    (1U << 1)
#define BMSR_EXTENDED_CAP     (1U << 0)

/* Біти ANAR та ANLPAR (Регістри 4 та 5) */
#define ANAR_NEXT_PAGE        (1U << 15)
#define ANAR_REMOTE_FAULT     (1U << 13)
#define ANAR_PAUSE_ASYM       (1U << 11)
#define ANAR_PAUSE_SYM        (1U << 10)
#define ANAR_100_TX_FD        (1U << 8)
#define ANAR_100_TX_HD        (1U << 7)
#define ANAR_10_T_FD          (1U << 6)
#define ANAR_10_T_HD          (1U << 5)
#define ANAR_SELECTOR_802_3   (0x0001U)

/* Біти 1000BASE-T Control (Регістр 9) */
#define CR1000_MS_MANUAL_EN   (1U << 12)
#define CR1000_MS_VALUE       (1U << 11)
#define CR1000_PORT_REPEATER  (1U << 10)
#define CR1000_FULL_DUPLEX    (1U << 9)
#define CR1000_HALF_DUPLEX    (1U << 8)

/* Домени MMD Clause 45 (DEVAD) */
#define MDIO_MMD_PMAPMD       1U
#define MDIO_MMD_WIS          2U
#define MDIO_MMD_PCS          3U
#define MDIO_MMD_PHYXS        4U
#define MDIO_MMD_DTEXS        5U
#define MDIO_MMD_AUTONEG      7U
#define MDIO_MMD_VEND1        29U
#define MDIO_MMD_VEND2        30U

/* Маски непрямого доступу MMD Control (Регістр 13) */
#define MMD_CTRL_FUNC_ADDR    (0x0U << 14)
#define MMD_CTRL_FUNC_DATA    (0x1U << 14)
#define MMD_CTRL_FUNC_DATA_PI (0x2U << 14)
#define MMD_CTRL_DEVAD_MASK   0x001FU

#endif /* PHY_REGISTERS_H */
