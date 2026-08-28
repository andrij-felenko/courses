#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів MCP23017 (BANK = 0) */
#define MCP_IODIRA    0x00
#define MCP_IODIRB    0x01
#define MCP_IPOLA     0x02
#define MCP_IPOLB     0x03
#define MCP_GPINTENA  0x04
#define MCP_GPINTENB  0x05
#define MCP_DEFVALA   0x06
#define MCP_DEFVALB   0x07
#define MCP_INTCONA   0x08
#define MCP_INTCONB   0x09
#define MCP_IOCON     0x0A
#define MCP_GPPUA     0x0C
#define MCP_GPPUB     0x0D
#define MCP_INTFA     0x0E
#define MCP_INTFB     0x0F
#define MCP_INTCAPA   0x10
#define MCP_INTCAPB   0x11
#define MCP_GPIOA     0x12
#define MCP_GPIOB     0x13
#define MCP_OLATA     0x14
#define MCP_OLATB     0x15

/* Біти конфігурації IOCON */
#define IOCON_MIRROR  (1 << 6)
#define IOCON_ODR     (1 << 2)
#define IOCON_INTPOL  (1 << 1)

typedef int (*i2c_write_fn)(uint8_t dev_addr, uint8_t reg, const uint8_t *data, uint16_t len);
typedef int (*i2c_read_fn)(uint8_t dev_addr, uint8_t reg, uint8_t *data, uint16_t len);

typedef struct {
    uint8_t dev_addr;
    i2c_write_fn write;
    i2c_read_fn read;
    uint16_t shadow_olat;     /* Тіньовий стан виходів A і B */
    uint16_t shadow_iodir;    /* Тіньовий напрямок пінів */
} mcp23017_t;

int mcp23017_init(mcp23017_t *dev, uint8_t i2c_addr, i2c_write_fn w_fn, i2c_read_fn r_fn) {
    dev->dev_addr = i2c_addr;
    dev->write = w_fn;
    dev->read = r_fn;
    dev->shadow_olat = 0x0000;
    dev->shadow_iodir = 0xFFFF; /* Усі входи за замовчуванням */

    /* Налаштування IOCON: об'єднати переривання A/B (MIRROR) та відкритий стік (ODR) */
    uint8_t iocon_val = IOCON_MIRROR | IOCON_ODR;
    return dev->write(dev->dev_addr, MCP_IOCON, &iocon_val, 1);
}

int mcp23017_set_pin_mode(mcp23017_t *dev, uint8_t pin, bool is_input, bool pullup) {
    if (pin >= 16) return -1;

    if (is_input) {
        dev->shadow_iodir |= (1 << pin);
    } else {
        dev->shadow_iodir &= ~(1 << pin);
    }

    uint8_t iodir_bytes[2] = {
        (uint8_t)(dev->shadow_iodir & 0xFF),
        (uint8_t)((dev->shadow_iodir >> 8) & 0xFF)
    };
    int err = dev->write(dev->dev_addr, MCP_IODIRA, iodir_bytes, 2);
    if (err != 0) return err;

    if (is_input && pullup) {
        uint8_t gppu_reg = (pin < 8) ? MCP_GPPUA : MCP_GPPUB;
        uint8_t bit_mask = 1 << (pin % 8);
        uint8_t current_gppu = 0;
        dev->read(dev->dev_addr, gppu_reg, &current_gppu, 1);
        current_gppu |= bit_mask;
        return dev->write(dev->dev_addr, gppu_reg, &current_gppu, 1);
    }
    return 0;
}

int mcp23017_write_pin(mcp23017_t *dev, uint8_t pin, bool level) {
    if (pin >= 16) return -1;

    if (level) {
        dev->shadow_olat |= (1 << pin);
    } else {
        dev->shadow_olat &= ~(1 << pin);
    }

    uint8_t reg = (pin < 8) ? MCP_OLATA : MCP_OLATB;
    uint8_t byte_val = (pin < 8) ? (dev->shadow_olat & 0xFF) : ((dev->shadow_olat >> 8) & 0xFF);
    return dev->write(dev->dev_addr, reg, &byte_val, 1);
}

int mcp23017_enable_interrupt(mcp23017_t *dev, uint8_t pin) {
    if (pin >= 16) return -1;
    uint8_t reg = (pin < 8) ? MCP_GPINTENA : MCP_GPINTENB;
    uint8_t val = 0;
    dev->read(dev->dev_addr, reg, &val, 1);
    val |= (1 << (pin % 8));
    return dev->write(dev->dev_addr, reg, &val, 1);
}

int mcp23017_read_captured_interrupt(mcp23017_t *dev, uint16_t *flags, uint16_t *captured_levels) {
    uint8_t intf[2] = {0, 0};
    uint8_t intcap[2] = {0, 0};

    /* Зчитування прапорців, хто викликав переривання */
    int err = dev->read(dev->dev_addr, MCP_INTFA, intf, 2);
    if (err != 0) return err;

    /* Зчитування зафіксованих логічних рівнів (це також скидає лінію /INT) */
    err = dev->read(dev->dev_addr, MCP_INTCAPA, intcap, 2);
    if (err != 0) return err;

    *flags = (uint16_t)intf[0] | ((uint16_t)intf[1] << 8);
    *captured_levels = (uint16_t)intcap[0] | ((uint16_t)intcap[1] << 8);
    return 0;
}
