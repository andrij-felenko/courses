#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define REPORT_TIMEOUT_MS   2000    // скільки чекаємо на цілий рапорт
#define LINE_MAX            200

// Читати символи, доки не трапиться '\n' або не вичерпається час.
// Повертає: true — рядок зібрано; false — вийшов таймаут.
bool jig_read_line(char *buf, size_t maxlen, uint32_t timeout_ms) {
    uint32_t start = jig_millis();
    size_t len = 0;

    while ((jig_millis() - start) < timeout_ms) {
        int c = uart_getc_nonblock();     // -1, якщо байта ще нема
        if (c < 0) continue;

        if (c == '\n' || c == '\r') {
            if (len == 0) continue;       // порожні кінці рядків пропускаємо
            buf[len] = '\0';
            return true;                  // цілий рядок зібрано
        }
        if (len < maxlen - 1) {
            buf[len++] = (char)c;
        }
        // якщо рядок довший за буфер — «зайве» тихо відкидаємо
    }
    return false;                         // час вийшов, цілого рядка нема
}
