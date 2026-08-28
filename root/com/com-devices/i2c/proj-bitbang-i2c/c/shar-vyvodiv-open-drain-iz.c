#include <avr/io.h>
#include <stdint.h>
#include <stdbool.h>

#define SDA_BIT 4          /* PC4 */
#define SCL_BIT 5          /* PC5 */

void i2c_pins_init(void) {
    /* засувка виходу = 0 назавжди; для входу цей же нуль вимикає
       внутрішню підтяжку — вона надто слабка, підтяжки мають бути зовнішні */
    PORTC &= ~((1 << SDA_BIT) | (1 << SCL_BIT));
    DDRC  &= ~((1 << SDA_BIT) | (1 << SCL_BIT));   /* обидві ніжки відпущено */
}

static inline void sda_low(void)     { DDRC |=  (1 << SDA_BIT); }   /* вихід → «0» */
static inline void sda_release(void) { DDRC &= ~(1 << SDA_BIT); }   /* вхід  → відпущено */
static inline bool sda_read(void)    { return (PINC >> SDA_BIT) & 1; }

static inline void scl_low(void)     { DDRC |=  (1 << SCL_BIT); }
static inline void scl_release(void) { DDRC &= ~(1 << SCL_BIT); }
static inline bool scl_read(void)    { return (PINC >> SCL_BIT) & 1; }
