#include <sys/random.h>
#include <errno.h>
#include <stdint.h>

uint8_t key[32];
ssize_t n;

do {
	n = getrandom(key, sizeof key, 0);   /* 0 — почекати готовності, далі не чекати */
} while (n < 0 && errno == EINTR);

if (n != (ssize_t)sizeof key)
	fatal();   /* лишилися тільки ENOSYS (ядро < 3.17) і EFAULT — обидві невиправні */
