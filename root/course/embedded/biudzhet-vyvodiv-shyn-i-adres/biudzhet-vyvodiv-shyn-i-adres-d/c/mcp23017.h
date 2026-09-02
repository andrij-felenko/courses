#ifndef MCP23017_H
#define MCP23017_H

#include "platform.h"

#define MCP23017_ADDR_BASE 0x20u  /* A2..A0 = 000; діапазон 0x20..0x27 */
#define MCP23017_MAX_CHIPS 8u

/* Порт A — входи (кінцевики, кнопки), порт B — виходи (реле).
   Саме такий розподіл описано в бюджеті плати реєстратора. */
typedef struct {
    uint8_t addr;
    uint8_t in_mask;      /* IODIRA: 1 = вхід */
    uint8_t pullup_mask;  /* GPPUA: внутрішні 100 кОм */
    uint8_t invert_mask;  /* IPOLA: замикання на землю читати як 1 */
    uint8_t int_mask;     /* GPINTENA: які входи будять лінію INT */
    uint8_t relay_shadow; /* тіньова копія OLATB */
} mcp23017_t;

io_status_t mcp23017_init(mcp23017_t *dev);
io_status_t mcp23017_relays(mcp23017_t *dev, uint8_t mask);
io_status_t mcp23017_relay_set(mcp23017_t *dev, uint8_t index, bool on);
io_status_t mcp23017_read_inputs(const mcp23017_t *dev, uint8_t *level);

/* Знімає подію з чипа: flags — які піни її викликали, captured — зліпок
   входів на момент перепаду. flags == 0 означає «лінію тримав не я». */
io_status_t mcp23017_take_event(mcp23017_t *dev, uint8_t *flags,
                                uint8_t *captured);

typedef struct {
    uint8_t addr;
    uint8_t flags;
    uint8_t captured;
} expander_event_t;

/* Кілька розширювачів, чиї виходи INT з відкритим стоком зведені монтажним
   «АБО» на один вхід переривання мікроконтролера. */
typedef struct {
    mcp23017_t *chip;
    uint8_t     count;
    uint8_t     int_pin;  /* спільна лінія INT на вході EXTI */
} expander_bank_t;

bool expander_bank_pending(const expander_bank_t *bank);

/* Обходить чипи, доки спільна лінія не підніметься. Повертає кількість
   складених у out подій; status (якщо не NULL) дістає першу помилку. */
uint8_t expander_bank_service(expander_bank_t *bank, expander_event_t *out,
                              uint8_t max, io_status_t *status);

#endif /* MCP23017_H */
