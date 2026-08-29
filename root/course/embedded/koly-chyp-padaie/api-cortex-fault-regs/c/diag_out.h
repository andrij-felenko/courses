/* diag_out.h — мінімальний синхронний вивід діагностики через ITM/SWO.
 *
 * У обробнику збою не можна користуватися printf: він тягне malloc, буфери
 * та блокування, а ми стоїмо у виняткові з пошкодженим стеком. Тому весь
 * вивід тут — посимвольний, без стану й без пам'яті на купі.
 */
#ifndef DIAG_OUT_H
#define DIAG_OUT_H

#include <stdint.h>
#include <stddef.h>

/* Опис одного прапорця регістра: маска, ім'я в довіднику й пояснення. */
struct diag_flag {
    uint32_t    mask;
    const char *name;
    const char *text;
};

void diag_puts(const char *s);
void diag_nl(void);

void diag_hex32(uint32_t v);
void diag_u32(uint32_t v);

/* "NAME = 0x00000000" з переводом рядка. */
void diag_reg(const char *name, uint32_t value);

/* Перебирає таблицю прапорців і друкує лише ті, що стоять у value.
 * Повертає кількість надрукованих — нуль означає «регістр чистий». */
size_t diag_flags(const struct diag_flag *table, size_t count, uint32_t value);

#endif /* DIAG_OUT_H */
