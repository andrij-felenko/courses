#include <stdint.h>
#include <stdbool.h>

/* Регістри IEEE 802.3 Clause 22 */
#define MDIO_REG_BMCR       0x00
#define MDIO_REG_BMSR       0x01
#define MDIO_REG_PHYID1     0x02
#define MDIO_REG_PHYID2     0x03
#define MDIO_REG_ANAR       0x04
#define MDIO_REG_ANLPAR     0x05
#define MDIO_REG_GBCR       0x09
#define MDIO_REG_GBSR       0x0A

/* Біти керування BMCR (0x00) */
#define BMCR_RESET          (1U << 15)
#define BMCR_SPEED_100      (1U << 13)
#define BMCR_AN_ENABLE      (1U << 12)
#define BMCR_AN_RESTART     (1U << 9)
#define BMCR_FULL_DUPLEX    (1U << 8)
#define BMCR_SPEED_1000     (1U << 6)

/* Біти статусу BMSR (0x01) */
#define BMSR_AN_COMPLETE    (1U << 5)
#define BMSR_LINK_STATUS    (1U << 2)

/* Біти здатностей ANAR / ANLPAR */
#define ADVERTISE_PAUSE_ASYM (1U << 11)
#define ADVERTISE_PAUSE_SYM  (1U << 10)
#define ADVERTISE_100_FULL   (1U << 8)
#define ADVERTISE_100_HALF   (1U << 7)
#define ADVERTISE_10_FULL    (1U << 6)
#define ADVERTISE_10_HALF    (1U << 5)
#define ADVERTISE_CSMA       (1U << 0)

/* Біти гігабітного керування та статусу */
#define GBCR_ADV_1000_FULL   (1U << 9)
#define GBCR_ADV_1000_HALF   (1U << 8)
#define GBSR_LP_1000_FULL    (1U << 11)
#define GBSR_LP_1000_HALF    (1U << 10)

typedef enum {
    LINK_SPEED_UNKNOWN = 0,
    LINK_SPEED_10M     = 10,
    LINK_SPEED_100M    = 100,
    LINK_SPEED_1000M   = 1000
} LinkSpeed;

typedef enum {
    LINK_DUPLEX_HALF = 0,
    LINK_DUPLEX_FULL = 1
} LinkDuplex;

typedef struct {
    bool link_up;
    LinkSpeed speed;
    LinkDuplex duplex;
    bool pause_rx;
    bool pause_tx;
} LinkStatus;

/* Апаратні операції GPIO (реалізуються для конкретної платформи) */
typedef struct {
    void (*set_mdc)(bool level);
    void (*set_mdio_dir_out)(bool out);
    void (*set_mdio_data)(bool level);
    bool (*get_mdio_data)(void);
    void (*delay_half_period)(void); /* Затримка ~200 нс (для MDC = 2.5 МГц) */
} MdioGpioOps;

typedef struct {
    const MdioGpioOps *ops;
    uint8_t phy_addr;
} EthernetPhyDriver;

/* Допоміжні функції побітового зв'язку */
static void mdio_clock_cycle(const MdioGpioOps *ops) {
    ops->set_mdc(false);
    ops->delay_half_period();
    ops->set_mdc(true);
    ops->delay_half_period();
}

static void mdio_send_bits(const MdioGpioOps *ops, uint32_t value, uint8_t count) {
    for (int8_t i = (int8_t)(count - 1); i >= 0; --i) {
        ops->set_mdc(false);
        ops->set_mdio_data((value >> i) & 1U);
        ops->delay_half_period();
        ops->set_mdc(true);
        ops->delay_half_period();
    }
}

static void mdio_send_preamble(const MdioGpioOps *ops) {
    ops->set_mdio_dir_out(true);
    ops->set_mdio_data(true);
    for (uint8_t i = 0; i < 32; ++i) {
        mdio_clock_cycle(ops);
    }
}

/* Читання регістра Clause 22 */
bool mdio_read(const EthernetPhyDriver *phy, uint8_t reg_addr, uint16_t *value) {
    const MdioGpioOps *ops = phy->ops;
    mdio_send_preamble(ops);

    /* ST=01 (2 біти), OP=10 (читання, 2 біти) */
    mdio_send_bits(ops, 0x01, 2);
    mdio_send_bits(ops, 0x02, 2);

    /* PHYAD (5 бітів), REGAD (5 бітів) */
    mdio_send_bits(ops, phy->phy_addr, 5);
    mdio_send_bits(ops, reg_addr, 5);

    /* Turnaround: перемикаємося на вхід */
    ops->set_mdio_dir_out(false);
    
    /* Такт 1 фази TA (стан Z) */
    ops->set_mdc(false);
    ops->delay_half_period();
    ops->set_mdc(true);
    ops->delay_half_period();

    /* Такт 2 фази TA: перевіряємо, чи притиснув PHY лінію до нуля */
    ops->set_mdc(false);
    ops->delay_half_period();
    bool ack = (ops->get_mdio_data() == false);
    ops->set_mdc(true);
    ops->delay_half_period();

    if (!ack) {
        return false; /* PHY не відповів на запит */
    }

    /* Читання 16 бітів даних */
    uint16_t data = 0;
    for (uint8_t i = 0; i < 16; ++i) {
        ops->set_mdc(false);
        ops->delay_half_period();
        data = (data << 1) | (ops->get_mdio_data() ? 1U : 0U);
        ops->set_mdc(true);
        ops->delay_half_period();
    }

    /* Додатковий такт для повернення шини в стан спокою */
    mdio_clock_cycle(ops);

    *value = data;
    return true;
}

/* Запис регістра Clause 22 */
bool mdio_write(const EthernetPhyDriver *phy, uint8_t reg_addr, uint16_t value) {
    const MdioGpioOps *ops = phy->ops;
    mdio_send_preamble(ops);

    /* ST=01 (2 біти), OP=01 (запис, 2 біти) */
    mdio_send_bits(ops, 0x01, 2);
    mdio_send_bits(ops, 0x01, 2);

    /* PHYAD (5 бітів), REGAD (5 бітів) */
    mdio_send_bits(ops, phy->phy_addr, 5);
    mdio_send_bits(ops, reg_addr, 5);

    /* TA = 10b (2 біти) */
    mdio_send_bits(ops, 0x02, 2);

    /* 16 бітів даних */
    mdio_send_bits(ops, value, 16);

    /* Відпускаємо шину */
    ops->set_mdio_dir_out(false);
    mdio_clock_cycle(ops);
    return true;
}

/* Ініціалізація та налаштування автопогодження */
bool phy_init(const EthernetPhyDriver *phy) {
    uint16_t val = 0;

    /* Перевіряємо присутність чіпа */
    if (!mdio_read(phy, MDIO_REG_PHYID1, &val) || val == 0xFFFF || val == 0x0000) {
        return false;
    }

    /* Запускаємо програмне скидання */
    mdio_write(phy, MDIO_REG_BMCR, BMCR_RESET);
    for (int timeout = 0; timeout < 100; ++timeout) {
        if (mdio_read(phy, MDIO_REG_BMCR, &val) && !(val & BMCR_RESET)) {
            break;
        }
    }

    /* Оголошуємо всі швидкості 10/100/1000 та підтримку PAUSE */
    uint16_t anar = ADVERTISE_CSMA | ADVERTISE_10_HALF | ADVERTISE_10_FULL |
                    ADVERTISE_100_HALF | ADVERTISE_100_FULL |
                    ADVERTISE_PAUSE_SYM | ADVERTISE_PAUSE_ASYM;
    mdio_write(phy, MDIO_REG_ANAR, anar);

    uint16_t gbcr = GBCR_ADV_1000_FULL | GBCR_ADV_1000_HALF;
    mdio_write(phy, MDIO_REG_GBCR, gbcr);

    /* Запускаємо автопогодження */
    uint16_t bmcr = BMCR_AN_ENABLE | BMCR_AN_RESTART;
    mdio_write(phy, MDIO_REG_BMCR, bmcr);

    return true;
}

/* Опитування стану та пріоритетне розв'язання параметрів лінка */
LinkStatus phy_poll_status(const EthernetPhyDriver *phy) {
    LinkStatus status = {0};
    uint16_t bmsr = 0;

    /* Перше читання скидає засувку Latching Low, друге дає реальний статус */
    mdio_read(phy, MDIO_REG_BMSR, &bmsr);
    if (!mdio_read(phy, MDIO_REG_BMSR, &bmsr) || !(bmsr & BMSR_LINK_STATUS)) {
        status.link_up = false;
        return status;
    }

    status.link_up = true;

    /* Якщо автопогодження не завершено, параметри ще не визначено */
    if (!(bmsr & BMSR_AN_COMPLETE)) {
        status.speed = LINK_SPEED_UNKNOWN;
        return status;
    }

    /* Зчитуємо локальні та віддалені здатності */
    uint16_t gbcr = 0, gbsr = 0, anar = 0, anlpar = 0;
    mdio_read(phy, MDIO_REG_GBCR, &gbcr);
    mdio_read(phy, MDIO_REG_GBSR, &gbsr);
    mdio_read(phy, MDIO_REG_ANAR, &anar);
    mdio_read(phy, MDIO_REG_ANLPAR, &anlpar);

    /* Таблиця пріоритетів IEEE 802.3 */
    if ((gbcr & GBCR_ADV_1000_FULL) && (gbsr & GBSR_LP_1000_FULL)) {
        status.speed = LINK_SPEED_1000M;
        status.duplex = LINK_DUPLEX_FULL;
    } else if ((gbcr & GBCR_ADV_1000_HALF) && (gbsr & GBSR_LP_1000_HALF)) {
        status.speed = LINK_SPEED_1000M;
        status.duplex = LINK_DUPLEX_HALF;
    } else if ((anar & ADVERTISE_100_FULL) && (anlpar & ADVERTISE_100_FULL)) {
        status.speed = LINK_SPEED_100M;
        status.duplex = LINK_DUPLEX_FULL;
    } else if ((anar & ADVERTISE_100_HALF) && (anlpar & ADVERTISE_100_HALF)) {
        status.speed = LINK_SPEED_100M;
        status.duplex = LINK_DUPLEX_HALF;
    } else if ((anar & ADVERTISE_10_FULL) && (anlpar & ADVERTISE_10_FULL)) {
        status.speed = LINK_SPEED_10M;
        status.duplex = LINK_DUPLEX_FULL;
    } else if ((anar & ADVERTISE_10_HALF) && (anlpar & ADVERTISE_10_HALF)) {
        status.speed = LINK_SPEED_10M;
        status.duplex = LINK_DUPLEX_HALF;
    }

    /* Обчислення режиму керування потоком PAUSE (IEEE 802.3 Annex 28B) */
    bool loc_sym = (anar & ADVERTISE_PAUSE_SYM) != 0;
    bool loc_asym = (anar & ADVERTISE_PAUSE_ASYM) != 0;
    bool lp_sym = (anlpar & ADVERTISE_PAUSE_SYM) != 0;
    bool lp_asym = (anlpar & ADVERTISE_PAUSE_ASYM) != 0;

    if (loc_sym && lp_sym) {
        status.pause_rx = true;
        status.pause_tx = true;
    } else if (loc_asym && lp_sym && lp_asym) {
        status.pause_rx = true;
        status.pause_tx = false;
    } else if (loc_sym && loc_asym && lp_asym) {
        status.pause_rx = false;
        status.pause_tx = true;
    }

    return status;
}
