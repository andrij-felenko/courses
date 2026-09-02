#ifndef SERIAL_H
#define SERIAL_H

#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>
#include <termios.h>

/* Відкриває UART у «сирому» режимі (cfmakeraw): без канонізації, ехо
 * та підміни CR/LF. MAVLink двійковий — будь-яка обробка байтів
 * термінальним рівнем псує кадр. Повертає дескриптор або -1 (errno). */
int serial_open(const char *port, speed_t baud);

/* Пише буфер ПОВНІСТЮ: переживає часткові записи, EINTR і EAGAIN.
 * timeout_ms обмежує чекання на місце в буфері драйвера — інакше
 * забитий UART з'їв би такт циклу 20 Гц.
 * 0 — усе записано; -1 — помилка або таймаут (errno). */
int serial_write_all(int fd, const uint8_t *data, size_t len, int timeout_ms);

/* Забирає те, що вже лежить у буфері драйвера, не блокуючись.
 * Кількість байтів, 0 — порожньо, -1 — помилка. */
ssize_t serial_read_available(int fd, uint8_t *buf, size_t cap);

void serial_close(int fd);

#endif /* SERIAL_H */
