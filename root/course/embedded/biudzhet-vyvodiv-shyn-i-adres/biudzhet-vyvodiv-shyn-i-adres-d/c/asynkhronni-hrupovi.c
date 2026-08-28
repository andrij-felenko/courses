#include <stdint.h>
#include <stdbool.h>

#define MCP23017_ADDR       0x20

/* Регістри MCP23017 (для банку IOCON.BANK = 0) */
#define REG_IODIRA          0x00
#define REG_GPINTENA        0x04
#define REG_INTFA           0x0E
#define REG_INTCAPA         0x10
#define REG_GPIOA           0x12

extern bool i2c_write_reg(uint8_t dev, uint8_t reg, uint8_t val);
extern bool i2c_read_reg(uint8_t dev, uint8_t reg, uint8_t *val);

/* Ініціалізація порту A MCP23017 на генерацію переривань */
bool mcp23017_init_interrupts(uint8_t dev_addr) {
    /* 1. Всі піни порту A як входи */
    if (!i2c_write_reg(dev_addr, REG_IODIRA, 0xFF)) return false;

    /* 2. Дозволити переривання при зміні рівня на всіх 8 пінах */
    if (!i2c_write_reg(dev_addr, REG_GPINTENA, 0xFF)) return false;

    /* 3. Очистити можливі початкові прапорці шляхом зчитування порту */
    uint8_t dummy;
    return i2c_read_reg(dev_addr, REG_GPIOA, &dummy);
}

/* Обробник нижньої половини переривання (викликається з головного циклу/задачі) */
bool mcp23017_process_interrupt(uint8_t dev_addr, uint8_t *triggered_pins, uint8_t *captured_state) {
    /* Зчитуємо прапорець: який саме пін викликав подію */
    if (!i2c_read_reg(dev_addr, REG_INTFA, triggered_pins)) return false;

    /* Зчитуємо зафіксований стан у момент події (це також скидає лінію INT чипа) */
    if (!i2c_read_reg(dev_addr, REG_INTCAPA, captured_state)) return false;

    return true;
}
