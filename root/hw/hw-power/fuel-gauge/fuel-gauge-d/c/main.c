#include <stdint.h>

#define MAX17048_ADDR   0x36u   /* 7-бітна адреса в шині           */
#define REG_VCELL       0x02u   /* напруга комірки, 2 байти        */
#define REG_SOC         0x04u   /* стан заряду, 2 байти            */

/* hal_i2c_read_u16: прочитати 2 байти з регістра reg, повернути їх
   як 16-бітне ціле зі старшим байтом попереду (big-endian чипа). */
static uint16_t reg_read_u16(uint8_t reg)
{
    uint8_t b[2];
    hal_i2c_read(MAX17048_ADDR, reg, b, 2);   /* ваша HAL-обгортка I²C */
    return ((uint16_t)b[0] << 8) | b[1];      /* старший байт — перший */
}

/* SoC у відсотках: регістр має роздільність 1/256 % */
float max17048_soc(void)
{
    return reg_read_u16(REG_SOC) / 256.0f;
}

/* Напруга комірки у вольтах: крок АЦП 78.125 мкВ на молодший біт */
float max17048_vcell(void)
{
    return reg_read_u16(REG_VCELL) * 78.125e-6f;
}
