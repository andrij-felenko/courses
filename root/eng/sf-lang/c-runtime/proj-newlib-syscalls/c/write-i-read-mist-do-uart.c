#include <unistd.h>
#include "driver/uart.h"          // приклад під ESP-IDF; ідея спільна для будь-якого UART

int _write(int fd, const char *buf, int len) {
    if (fd != STDOUT_FILENO && fd != STDERR_FILENO) {
        errno = EBADF;            // у нас лише консоль; інші дескриптори невідомі
        return -1;
    }
    uart_write_bytes(UART_NUM_0, buf, len);
    return len;                   // скільки байтів прийняли (тут — усі)
}

int _read(int fd, char *buf, int len) {
    if (fd != STDIN_FILENO) { errno = EBADF; return -1; }
    int n = uart_read_bytes(UART_NUM_0, (uint8_t *)buf, len, pdMS_TO_TICKS(20));
    return n < 0 ? 0 : n;         // 0 = «поки нема даних» (EOF-семантика для stdin)
}
