#ifndef BQ2419X_REGS_H
#define BQ2419X_REGS_H
#include <stdint.h>

#define BQ_ADDR   0x6B          /* 7-бітна адреса bq2419x на шині */

/* Іменовані регістри (bq2419x, за даташитом SLUSAW5B) */
#define BQ_REG00  0x00
#define BQ_REG01  0x01
#define BQ_REG02  0x02
#define BQ_REG03  0x03
#define BQ_REG04  0x04
#define BQ_REG05  0x05
#define BQ_REG08  0x08
#define BQ_REG09  0x09
#define BQ_REG0A  0x0A

/* Маски й іменовані значення полів */
#define REG00_IINLIM_MASK      0x07
#define REG01_REG_RST          (1u << 7)
#define REG01_WD_RST           (1u << 6)
#define REG01_CHG_CONFIG_MASK  0x30
#define REG01_CHG_ENABLE       0x10        /* CHG_CONFIG = 01 */
#define REG02_ICHG_MASK        0xFC        /* біти [7:2] */
#define REG03_ITERM_MASK       0x0F        /* біти [3:0] */
#define REG04_VREG_MASK        0xFC        /* біти [7:2] */
#define REG05_EN_TERM          (1u << 7)

/* IINLIM: найбільший табличний щабель, що НЕ перевищує ma */
static inline uint8_t iinlim_code(uint16_t ma)
{
    static const uint16_t tbl[8] = {100, 150, 500, 900, 1200, 1500, 2000, 3000};
    uint8_t code = 0;
    for (uint8_t i = 0; i < 8; i++)
        if (tbl[i] <= ma) code = i;
    return code;                            /* 000…111 */
}

/* ICHG: зсув 512 мА, крок 64 мА, поле [7:2]; округлення вниз */
static inline uint8_t ichg_reg(uint16_t ma)
{
    if (ma < 512)  ma = 512;
    if (ma > 4544) ma = 4544;
    return (uint8_t)(((ma - 512) / 64) << 2);
}

/* VREG: зсув 3504 мВ, крок 16 мВ, поле [7:2]; округлення вниз (не вище потолку) */
static inline uint8_t vreg_reg(uint16_t mv)
{
    if (mv < 3504) mv = 3504;
    if (mv > 4400) mv = 4400;
    return (uint8_t)(((mv - 3504) / 16) << 2);
}

/* ITERM: зсув 128 мА, крок 128 мА, поле [3:0] */
static inline uint8_t iterm_code(uint16_t ma)
{
    if (ma < 128)  ma = 128;
    if (ma > 2048) ma = 2048;
    return (uint8_t)((ma - 128) / 128);
}

#endif /* BQ2419X_REGS_H */
