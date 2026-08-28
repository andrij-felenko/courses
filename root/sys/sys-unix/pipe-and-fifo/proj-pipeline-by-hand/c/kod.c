#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

/* Поставити fd на місце стандартного потоку slot і прибрати зайву копію.
   Випадок fd == slot окремий: dup2 тоді НЕ РОБИТЬ НІЧОГО і повертає slot,
   отже й прапорець FD_CLOEXEC лишається таким, як був. Знімаємо його руками,
   інакше exec закриє потік і програма прокинеться без stdout. */
static int move_to(int fd, int slot)
{
    if (fd == slot) {
        int fl = fcntl(fd, F_GETFD);
        return (fl < 0) ? -1 : fcntl(fd, F_SETFD, fl & ~FD_CLOEXEC);
    }
    if (dup2(fd, slot) < 0)     /* у копії під номером slot FD_CLOEXEC завжди знято */
        return -1;
    return close(fd);           /* close №1 і №2 з наших шести */
}
