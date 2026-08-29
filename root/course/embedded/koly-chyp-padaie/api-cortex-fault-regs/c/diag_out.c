#include "diag_out.h"

#include "stm32f4xx.h"   /* CMSIS: ITM, ITM_SendChar() */

/* ITM_SendChar() із CMSIS сам перевіряє, чи ввімкнено трасування
 * (ITM->TCR.ITMENA і дозвіл стимул-порту 0). Якщо відладчик не підключений,
 * символ тихо гине — і це правильно: діагностика не має вішати прошивку
 * очікуванням на порт, якого ніхто не читає. */
static void diag_putc(char c)
{
    if (c == '\n') {
        (void)ITM_SendChar('\r');
    }
    (void)ITM_SendChar((uint32_t)(unsigned char)c);
}

void diag_puts(const char *s)
{
    if (s == NULL) {
        s = "(null)";
    }
    while (*s != '\0') {
        diag_putc(*s++);
    }
}

void diag_nl(void)
{
    diag_putc('\n');
}

void diag_hex32(uint32_t v)
{
    static const char digits[] = "0123456789ABCDEF";
    char buf[11];

    buf[0] = '0';
    buf[1] = 'x';
    for (unsigned i = 0; i < 8u; ++i) {
        buf[2u + i] = digits[(v >> (28u - 4u * i)) & 0xFu];
    }
    buf[10] = '\0';

    diag_puts(buf);
}

void diag_u32(uint32_t v)
{
    char buf[11];
    unsigned pos = sizeof buf - 1u;

    buf[pos] = '\0';
    do {
        buf[--pos] = (char)('0' + (v % 10u));
        v /= 10u;
    } while (v != 0u && pos > 0u);

    diag_puts(&buf[pos]);
}

void diag_reg(const char *name, uint32_t value)
{
    diag_puts("  ");
    diag_puts(name);
    diag_puts(" = ");
    diag_hex32(value);
    diag_nl();
}

size_t diag_flags(const struct diag_flag *table, size_t count, uint32_t value)
{
    size_t shown = 0;

    for (size_t i = 0; i < count; ++i) {
        if ((value & table[i].mask) == 0u) {
            continue;
        }
        diag_puts("    * ");
        diag_puts(table[i].name);
        diag_puts(" — ");
        diag_puts(table[i].text);
        diag_nl();
        ++shown;
    }
    return shown;
}
