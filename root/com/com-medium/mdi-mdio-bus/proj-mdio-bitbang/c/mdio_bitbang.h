/* mdio_bitbang.h / mdio_bitbang.c - Повна реалізація драйвера Bit-Banging MDC/MDIO на C */
#ifndef MDIO_BITBANG_H
#define MDIO_BITBANG_H

#include <stdint.h>
#include <stdbool.h>

/* Абстракція низькорівневого доступу до ліній GPIO */
typedef struct {
    void (*set_mdc)(bool level);
    void (*set_mdio_level)(bool level);
    bool (*get_mdio_level)(void);
    void (*set_mdio_dir_output)(bool is_output);
    void (*delay_half_period)(void); /* Затримка ~200 нс для досягнення 2.5 МГц */
} mdio_gpio_ops_t;

typedef struct {
    mdio_gpio_ops_t ops;
} mdio_bus_t;

typedef enum {
    MDIO_OK = 0,
    MDIO_ERR_TIMEOUT,
    MDIO_ERR_NO_DEVICE,
    MDIO_ERR_INVALID_PARAM
} mdio_status_t;

void mdio_bb_init(const mdio_bus_t *bus);
mdio_status_t mdio_bb_c22_write(const mdio_bus_t *bus, uint8_t phy_addr, uint8_t reg_addr, uint16_t data);
mdio_status_t mdio_bb_c22_read(const mdio_bus_t *bus, uint8_t phy_addr, uint8_t reg_addr, uint16_t *data);
mdio_status_t mdio_bb_c45_write(const mdio_bus_t *bus, uint8_t prt_addr, uint8_t dev_addr, uint16_t reg_addr, uint16_t data);
mdio_status_t mdio_bb_c45_read(const mdio_bus_t *bus, uint8_t prt_addr, uint8_t dev_addr, uint16_t reg_addr, uint16_t *data);
uint32_t mdio_bb_scan(const mdio_bus_t *bus);
bool mdio_bb_get_link_status(const mdio_bus_t *bus, uint8_t phy_addr);

#endif /* MDIO_BITBANG_H */

/* --- Реалізація функцій драйвера --- */

static void mdc_pulse(const mdio_bus_t *bus) {
    bus->ops.set_mdc(true);
    bus->ops.delay_half_period();
    bus->ops.set_mdc(false);
    bus->ops.delay_half_period();
}

static void send_preamble(const mdio_bus_t *bus) {
    bus->ops.set_mdio_dir_output(true);
    bus->ops.set_mdio_level(true);
    for (int i = 0; i < 32; ++i) {
        mdc_pulse(bus);
    }
}

static void send_bits(const mdio_bus_t *bus, uint32_t value, uint8_t count) {
    for (int i = (int)count - 1; i >= 0; --i) {
        bool bit = (value >> i) & 1U;
        bus->ops.set_mdio_level(bit);
        bus->ops.delay_half_period();
        bus->ops.set_mdc(true);
        bus->ops.delay_half_period();
        bus->ops.set_mdc(false);
    }
}

static uint16_t receive_bits(const mdio_bus_t *bus, uint8_t count) {
    uint16_t res = 0;
    for (int i = 0; i < (int)count; ++i) {
        bus->ops.set_mdc(true);
        bus->ops.delay_half_period();
        res = (uint16_t)((res << 1) | (bus->ops.get_mdio_level() ? 1U : 0U));
        bus->ops.set_mdc(false);
        bus->ops.delay_half_period();
    }
    return res;
}

void mdio_bb_init(const mdio_bus_t *bus) {
    bus->ops.set_mdio_dir_output(true);
    bus->ops.set_mdio_level(true);
    bus->ops.set_mdc(false);
    bus->ops.delay_half_period();
}

mdio_status_t mdio_bb_c22_write(const mdio_bus_t *bus, uint8_t phy_addr, uint8_t reg_addr, uint16_t data) {
    if (phy_addr > 31 || reg_addr > 31) return MDIO_ERR_INVALID_PARAM;

    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);

    send_bits(bus, 0x01U, 2);        /* ST = 01 */
    send_bits(bus, 0x01U, 2);        /* OP = 01 (Write) */
    send_bits(bus, phy_addr, 5);     /* PHYAD */
    send_bits(bus, reg_addr, 5);     /* REGAD */
    send_bits(bus, 0x02U, 2);        /* TA = 10 */
    send_bits(bus, data, 16);        /* DATA */

    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);
    return MDIO_OK;
}

mdio_status_t mdio_bb_c22_read(const mdio_bus_t *bus, uint8_t phy_addr, uint8_t reg_addr, uint16_t *data) {
    if (!data || phy_addr > 31 || reg_addr > 31) return MDIO_ERR_INVALID_PARAM;

    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);

    send_bits(bus, 0x01U, 2);        /* ST = 01 */
    send_bits(bus, 0x02U, 2);        /* OP = 10 (Read) */
    send_bits(bus, phy_addr, 5);     /* PHYAD */
    send_bits(bus, reg_addr, 5);     /* REGAD */

    /* Turnaround: перехід у режим високоімпедансного входу */
    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);                  /* Такт Z */

    /* Зчитування біта підтвердження (ACK від PHY = 0) */
    bus->ops.set_mdc(true);
    bus->ops.delay_half_period();
    bool ack = bus->ops.get_mdio_level();
    bus->ops.set_mdc(false);
    bus->ops.delay_half_period();

    if (ack) return MDIO_ERR_NO_DEVICE;

    *data = receive_bits(bus, 16);
    mdc_pulse(bus);
    return MDIO_OK;
}

mdio_status_t mdio_bb_c45_write(const mdio_bus_t *bus, uint8_t prt_addr, uint8_t dev_addr, uint16_t reg_addr, uint16_t data) {
    if (prt_addr > 31 || dev_addr > 31) return MDIO_ERR_INVALID_PARAM;

    /* 1. Кадр адреси */
    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);
    send_bits(bus, 0x00U, 2);        /* ST = 00 (Clause 45) */
    send_bits(bus, 0x00U, 2);        /* OP = 00 (Address) */
    send_bits(bus, prt_addr, 5);
    send_bits(bus, dev_addr, 5);
    send_bits(bus, 0x02U, 2);        /* TA = 10 */
    send_bits(bus, reg_addr, 16);
    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);

    /* 2. Кадр запису даних */
    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);
    send_bits(bus, 0x00U, 2);        /* ST = 00 */
    send_bits(bus, 0x01U, 2);        /* OP = 01 (Write) */
    send_bits(bus, prt_addr, 5);
    send_bits(bus, dev_addr, 5);
    send_bits(bus, 0x02U, 2);        /* TA = 10 */
    send_bits(bus, data, 16);
    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);

    return MDIO_OK;
}

mdio_status_t mdio_bb_c45_read(const mdio_bus_t *bus, uint8_t prt_addr, uint8_t dev_addr, uint16_t reg_addr, uint16_t *data) {
    if (!data || prt_addr > 31 || dev_addr > 31) return MDIO_ERR_INVALID_PARAM;

    /* 1. Кадр адреси */
    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);
    send_bits(bus, 0x00U, 2);
    send_bits(bus, 0x00U, 2);
    send_bits(bus, prt_addr, 5);
    send_bits(bus, dev_addr, 5);
    send_bits(bus, 0x02U, 2);
    send_bits(bus, reg_addr, 16);
    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);

    /* 2. Кадр читання даних */
    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);
    send_bits(bus, 0x00U, 2);
    send_bits(bus, 0x03U, 2);        /* OP = 11 (Read) */
    send_bits(bus, prt_addr, 5);
    send_bits(bus, dev_addr, 5);

    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);

    bus->ops.set_mdc(true);
    bus->ops.delay_half_period();
    bool ack = bus->ops.get_mdio_level();
    bus->ops.set_mdc(false);
    bus->ops.delay_half_period();

    if (ack) return MDIO_ERR_NO_DEVICE;

    *data = receive_bits(bus, 16);
    mdc_pulse(bus);
    return MDIO_OK;
}

uint32_t mdio_bb_scan(const mdio_bus_t *bus) {
    uint32_t found_mask = 0;
    for (uint8_t addr = 0; addr < 32; ++addr) {
        uint16_t val = 0;
        if (mdio_bb_c22_read(bus, addr, 0x02, &val) == MDIO_OK) {
            if (val != 0xFFFFU && val != 0x0000U) {
                found_mask |= (1U << addr);
            }
        }
    }
    return found_mask;
}

bool mdio_bb_get_link_status(const mdio_bus_t *bus, uint8_t phy_addr) {
    uint16_t bmsr = 0;
    if (mdio_bb_c22_read(bus, phy_addr, 0x01, &bmsr) != MDIO_OK) return false;
    if (mdio_bb_c22_read(bus, phy_addr, 0x01, &bmsr) != MDIO_OK) return false;
    return (bmsr & (1U << 2)) != 0;
}
