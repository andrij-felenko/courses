#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t i2c_address;     /* Біти 0..3: базовий зсув адреси (0..15) */
    bool high_speed_mode;    /* Біт 4: прапорець високошвидкісного режиму */
    uint8_t operation_mode;  /* Біти 5..6: режим завантаження (0..3) */
    bool parity_enable;      /* Біт 7: перевірка парності */
} SystemConfig;

#define MASK_I2C_ADDR    0x0F /* 0b00001111 */
#define MASK_SPEED_MODE  0x10 /* 0b00010000 */
#define MASK_OPER_MODE   0x60 /* 0b01100000 */
#define MASK_PARITY_EN   0x80 /* 0b10000000 */

SystemConfig parse_dip_switches(uint8_t raw_gpio_byte) {
    /* 1. Інвертуємо байт для active-LOW (Pull-Up) схемотехніки */
    uint8_t active_high_byte = (uint8_t)(~raw_gpio_byte);
    
    SystemConfig config;
    /* 2. Виділяємо I2C адресу (біти 0..3) */
    config.i2c_address = active_high_byte & MASK_I2C_ADDR;
    
    /* 3. Виділяємо прапорець швидкості (біт 4) */
    config.high_speed_mode = (active_high_byte & MASK_SPEED_MODE) != 0;
    
    /* 4. Виділяємо режим роботи (біти 5..6) та зсуваємо на 5 позицій вправо */
    config.operation_mode = (uint8_t)((active_high_byte & MASK_OPER_MODE) >> 5);
    
    /* 5. Виділяємо прапорець парності (біт 7) */
    config.parity_enable = (active_high_byte & MASK_PARITY_EN) != 0;
    
    return config;
}
