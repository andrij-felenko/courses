/*
 * Регістрова карта акселерометра LIS2DH12 (ST). Внутрішній заголовок:
 * прикладний код його не включає — він бачить лише chip_driver.h.
 *
 * Числа взято з даташита LIS2DH12 (DocID027112) і апноти AN5005.
 */
#ifndef CHIP_REGS_H
#define CHIP_REGS_H

#include <stdint.h>

/* --- адреси регістрів --- */
#define CHIP_REG_WHO_AM_I     0x0Fu
#define CHIP_REG_CTRL1        0x20u
#define CHIP_REG_CTRL2        0x21u
#define CHIP_REG_CTRL3        0x22u
#define CHIP_REG_CTRL4        0x23u
#define CHIP_REG_CTRL5        0x24u
#define CHIP_REG_CTRL6        0x25u
#define CHIP_REG_STATUS       0x27u
#define CHIP_REG_OUT_X_L      0x28u
#define CHIP_REG_FIFO_CTRL    0x2Eu
#define CHIP_REG_FIFO_SRC     0x2Fu

#define CHIP_WHO_AM_I_VALUE   0x33u

/*
 * I2C багатобайтового автоінкремента сам не робить: старший біт адреси
 * регістру мусить бути виставлений, інакше пакетне читання шість разів
 * поверне той самий OUT_X_L. Це та деталь, через яку «читається лише X».
 */
#define CHIP_REG_AUTO_INC(reg) ((uint8_t)((reg) | 0x80u))

/* --- CTRL_REG1: ODR[7:4] | LPen[3] | Zen[2] | Yen[1] | Xen[0] --- */
#define CHIP_CTRL1_XYZ_EN     0x07u
#define CHIP_CTRL1_ODR_MASK   0xF0u
#define CHIP_CTRL1_ODR_SHIFT  4u
#define CHIP_CTRL1_LPEN       0x08u

/* --- CTRL_REG4: BDU[7] | BLE[6] | FS[5:4] | HR[3] | ST[2:1] | SIM[0] --- */
#define CHIP_CTRL4_BDU        0x80u
#define CHIP_CTRL4_FS_MASK    0x30u
#define CHIP_CTRL4_FS_SHIFT   4u
#define CHIP_CTRL4_HR         0x08u
#define CHIP_CTRL4_ST_MASK    0x06u
#define CHIP_CTRL4_ST_0       0x02u   /* self-test 0 */

/* --- CTRL_REG5: BOOT[7] | FIFO_EN[6] --- */
#define CHIP_CTRL5_BOOT       0x80u
#define CHIP_CTRL5_FIFO_EN    0x40u

/* --- STATUS_REG --- */
#define CHIP_STATUS_ZYXOR     0x80u   /* попередній відлік перезаписано */
#define CHIP_STATUS_ZYXDA     0x08u   /* готові всі три осі */

/* --- FIFO_CTRL_REG: FM[7:6] | TR[5] | FTH[4:0] --- */
#define CHIP_FIFO_MODE_BYPASS 0x00u
#define CHIP_FIFO_MODE_STREAM 0x80u

/* --- FIFO_SRC_REG: WTM[7] | OVRN[6] | EMPTY[5] | FSS[4:0] --- */
#define CHIP_FIFO_SRC_WTM     0x80u
#define CHIP_FIFO_SRC_OVRN    0x40u
#define CHIP_FIFO_SRC_EMPTY   0x20u
#define CHIP_FIFO_SRC_FSS     0x1Fu

/* Скидання BOOT піднімає з NVM заводські коефіцієнти підстроювання й
 * повертає CTRL_REG1..6 у ці значення. Розбіжність означає, що вміст
 * NVM не піднявся — калібрування недійсне. */
#define CHIP_CTRL1_RESET_VALUE 0x07u

#endif /* CHIP_REGS_H */
