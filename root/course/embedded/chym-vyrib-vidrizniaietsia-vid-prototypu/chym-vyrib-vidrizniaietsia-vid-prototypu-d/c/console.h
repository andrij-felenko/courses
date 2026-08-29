/* console.h — діагностичний порт (USART2, 115200 8N1).
 *
 * Ані переривань, ані DMA, ані кільцевого буфера: цей канал мусить
 * працювати в аварійній гілці, коли решті системи вже не довіряють. */
#ifndef CONSOLE_H
#define CONSOLE_H

#include <stddef.h>

void console_init(void);

/* Друк опитуванням із запобіжником на випадок мертвого передавача:
 * зависнути на очікуванні TXE у виробі не можна. */
void console_write_blocking(const char *data, size_t len);

void console_puts(const char *s);

#endif /* CONSOLE_H */
