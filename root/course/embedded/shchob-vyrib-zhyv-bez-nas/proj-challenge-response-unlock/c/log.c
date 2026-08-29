#include "log.h"

#include "hal.h"

static const char HEX_DIGITS[] = "0123456789ABCDEF";

/* Форматування робимо руками: printf у завантажувачі коштує кілька кілобайт Flash */
static void put(const char *text)
{
    size_t len = 0;
    while (text[len] != '\0') {
        len++;
    }
    hal_uart_write((const uint8_t *)text, len);
}

static void put_prefix(void)
{
    put("[BOOT] ");
}

void log_line(const char *text)
{
    put_prefix();
    put(text);
    put("\r\n");
}

void log_hex(const char *label, const uint8_t *data, size_t len)
{
    put_prefix();
    put(label);

    for (size_t i = 0; i < len; i++) {
        uint8_t pair[2] = {
            (uint8_t)HEX_DIGITS[data[i] >> 4],
            (uint8_t)HEX_DIGITS[data[i] & 0x0Fu],
        };
        hal_uart_write(pair, sizeof pair);
        if (i + 1 < len) {
            put(" ");
        }
    }

    put("\r\n");
}

void log_u32(const char *label, uint32_t value, const char *suffix)
{
    char digits[10];
    size_t pos = sizeof digits;

    if (value == 0) {
        digits[--pos] = '0';
    }
    while (value != 0) {
        digits[--pos] = (char)('0' + (value % 10u));
        value /= 10u;
    }

    put_prefix();
    put(label);
    hal_uart_write((const uint8_t *)&digits[pos], sizeof digits - pos);
    put(suffix);
    put("\r\n");
}

void log_addr(const char *label, uint32_t value, const char *suffix)
{
    uint8_t out[8];

    for (int i = 7; i >= 0; i--) {
        out[i] = (uint8_t)HEX_DIGITS[value & 0x0Fu];
        value >>= 4;
    }

    put_prefix();
    put(label);
    hal_uart_write(out, sizeof out);
    put(suffix);
    put("\r\n");
}
