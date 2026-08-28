#include <stdint.h>

#define FT_ADDR   0x38
#define FT_REG_NUM 0x02   // кількість дотиків
#define FT_REG_P1  0x03   // початок блоку першої точки

// примітиви платформи (HAL): повертають 0 при успіху
int i2c_read_regs(uint8_t addr, uint8_t reg, uint8_t *buf, uint32_t n);

typedef struct { uint16_t x, y; uint8_t touches; } touch_t;

int ft6206_read(touch_t *t) {
    uint8_t b[7];                                  // лічильник + 6 байтів точки
    if (i2c_read_regs(FT_ADDR, FT_REG_NUM, b, 7))  // читаємо 0x02..0x08 поспіль
        return -1;                                 // шина не відповіла

    t->touches = b[0] & 0x0F;                       // молодші біти — кількість
    if (t->touches == 0) { t->x = t->y = 0; return 0; }

    // координата 12-бітна: старший байт дає лише 4 біти, верхні — службові
    t->x = ((uint16_t)(b[1] & 0x0F) << 8) | b[2];   // b[1]=0x03, b[2]=0x04
    t->y = ((uint16_t)(b[3] & 0x0F) << 8) | b[4];   // b[3]=0x05, b[4]=0x06
    return 0;
}
