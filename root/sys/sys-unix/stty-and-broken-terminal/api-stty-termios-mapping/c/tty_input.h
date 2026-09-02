#ifndef TTY_INPUT_H
#define TTY_INPUT_H

#include <stddef.h>
#include <sys/types.h>

#define TTY_READ_ERROR       (-1)
#define TTY_READ_INTERRUPTED (-2)
#define TTY_DRAIN_EOF        (-2)

/* Куди віддавати вичитане. Один виклик — один read(). */
typedef void (*tty_chunk_fn)(const unsigned char *chunk, size_t len, void *user);

/* Вичитує все, що вже лежить у буфері ядра, до EAGAIN.
   Повертає кількість відданих байтів, TTY_DRAIN_EOF або TTY_READ_ERROR. */
ssize_t tty_drain(int fd, tty_chunk_fn on_chunk, void *user);

/* Один байт із блокуванням за правилами VMIN/VTIME.
   1 — прочитано; 0 — EOF; TTY_READ_INTERRUPTED — сигнал; TTY_READ_ERROR. */
int tty_read_byte(int fd, unsigned char *out);

/* write() має право записати менше, ніж просили, — дописуємо решту. */
int tty_write_all(int fd, const void *buf, size_t len);

int tty_set_nonblock(int fd, int on);
int tty_set_vmin_vtime(int fd, unsigned vmin, unsigned vtime);

#endif /* TTY_INPUT_H */
