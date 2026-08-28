#include <stdint.h>
#include <stddef.h>

/* Оголошення апаратних функцій конкретного чіпа */
extern void uart_send_byte_blocking(uint8_t ch);
extern void itm_send_byte(uint8_t ch);

/* Перевизначення системного виклику newlib libc */
int _write(int fd, const char *buf, int len) {
    /* Дескриптори 1 (stdout) та 2 (stderr) спрямовуємо в апаратний порт */
    if (fd == 1 || fd == 2) {
        for (int i = 0; i < len; ++i) {
            /* Автоматична заміна \n на послідовність \r\n для терміналів */
            if (buf[i] == '\n') {
                uart_send_byte_blocking((uint8_t)'\r');
            }
            uart_send_byte_blocking((uint8_t)buf[i]);
        }
        return len;
    }
    return -1;
}
