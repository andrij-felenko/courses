#ifndef RAWFRAME_H
#define RAWFRAME_H

#include <stdint.h>

/* Складання сирих відліків із буфера, знятого пакетним читанням.
   Буфер НІКОЛИ не розіменовуємо через (int16_t *): приймальна область DMA
   чи стековий масив uint8_t можуть стояти на непарній адресі, і ядро без
   апаратної підтримки непарного доступу віддасть HardFault. */

/* Порядок байтів у регістровій карті давача. */
uint16_t rf_u16_lsb_first(const uint8_t *p);
uint16_t rf_u16_msb_first(const uint8_t *p);
/* 20-бітний відлік (BMP280 і подібні): три байти, старший перший,
   значущі розряди 19..0 після зсуву службових чотирьох бітів. */
uint32_t rf_u20_msb_first(const uint8_t *p);

/* Три способи знакового розширення поля завширшки bits. */
int16_t rf_sign_extend_shift(uint16_t v, unsigned bits); /* подвійний зсув */
int16_t rf_sign_extend_mask(uint16_t v, unsigned bits);  /* маска 0xF000 */
int16_t rf_sign_extend_hw12(uint16_t v);                 /* SBFX, де є */

/* Розбір кадру трьох осей (шість байтів, по два на вісь).
   bits — кількість значущих розрядів АЦП (10, 12, 14 або 16). */
void rf_parse_left_aligned(const uint8_t buf[6], unsigned bits, int16_t out[3]);
void rf_parse_right_aligned(const uint8_t buf[6], unsigned bits, int16_t out[3]);
/* Давач із порядком MSB-first і повними 16 бітами (MPU6050 і рідня). */
void rf_parse_be16(const uint8_t buf[6], int16_t out[3]);

#endif /* RAWFRAME_H */
