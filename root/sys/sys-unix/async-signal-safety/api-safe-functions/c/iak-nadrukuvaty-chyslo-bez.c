#include <errno.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>

/* Цифри лягають з кінця буфера. Повертає вказівник на першу з них,
   довжину кладе в *len. Найдовше беззнакове 64-бітне число —
   18446744073709551615 — це рівно 20 цифр, тож буфер такий і беруть. */
static char *dec(unsigned long long v, char *end, size_t *len)
{
    char *p = end;
    do {
        *--p = (char) ('0' + v % 10);
        v /= 10;
    } while (v != 0);

    *len = (size_t) (end - p);
    return p;
}

static volatile sig_atomic_t hits;

static void on_signal(int signo)
{
    int saved = errno;                 /* чужий errno — під захист */
    char name[SIG2STR_MAX];
    char digits[20];
    char msg[3 + SIG2STR_MAX + 2 + 20 + 1];   /* "SIG" + ім'я + " #" + цифри + '\n' */
    size_t n = 0, dlen, nlen;
    char *d;

    hits++;
    d = dec((unsigned long long) hits, digits + sizeof digits, &dlen);

    if (sig2str(signo, name) != 0)
        strcpy(name, "?");
    nlen = strlen(name);

    memcpy(msg + n, "SIG", 3);  n += 3;
    memcpy(msg + n, name, nlen);  n += nlen;
    memcpy(msg + n, " #", 2);   n += 2;
    memcpy(msg + n, d, dlen);   n += dlen;
    msg[n++] = '\n';

    (void) write(STDERR_FILENO, msg, n);   /* один виклик, без буферів */

    errno = saved;
}
