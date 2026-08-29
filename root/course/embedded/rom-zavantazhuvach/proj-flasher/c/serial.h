#ifndef FLASHER_SERIAL_H
#define FLASHER_SERIAL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Відкритий послідовний порт у сирому режимі 115200 8E1.
   Саме такий кадр очікує ROM-завантажувач під час автопідлаштування бітрейту. */
typedef struct {
    int fd;
} serial_port;

/* Відкриває порт і переводить термінал у сирий 8E1. false → дивись errno. */
bool serial_open(serial_port *port, const char *path);
void serial_close(serial_port *port);

/* Пише рівно len байтів; часткові записи дописує сам. */
bool serial_write_all(const serial_port *port, const uint8_t *data, size_t len);

/* Читає рівно len байтів або віддає false, коли вичерпано спільний таймаут. */
bool serial_read_exact(const serial_port *port, uint8_t *buf, size_t len, unsigned timeout_ms);

/* Викидає все, що встигло накопичитися в буферах ядра (сміття після скидання). */
void serial_flush(const serial_port *port);

/* Апаратне входження в System Memory: BOOT0 = 1, імпульс NRST, пауза на HSI. */
bool serial_enter_bootloader(const serial_port *port);

#endif /* FLASHER_SERIAL_H */
