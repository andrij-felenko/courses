/* fdtour.c — прогулянка власною таблицею дескрипторів.
 *
 *   gcc -Wall -Wextra -O2 -o fdtour fdtour.c
 *
 * Потрібен Linux: усе, що ми розглядаємо, видно через /proc.
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

static void die(const char *what)
{
    fprintf(stderr, "!! %s: %s\n", what, strerror(errno));
    exit(EXIT_FAILURE);
}

static void banner(const char *title)
{
    printf("\n──── %s ────\n", title);
}

/* Збирає номери відкритих дескрипторів у масив. Повертає їхню кількість
 * або -1, якщо не вдалося навіть відкрити каталог (таке буває — див. дослід
 * із EMFILE). Номер, що його зайняв сам обхід, у перелік не потрапляє. */
static int list_fds(int *out, int max)
{
    DIR *d = opendir("/proc/self/fd");
    if (d == NULL)
        return -1;

    int own = dirfd(d);            /* номер, під яким відкрито сам каталог */
    if (own < 0) die("dirfd");

    int n = 0;
    for (;;) {
        errno = 0;
        struct dirent *e = readdir(d);
        if (e == NULL) {
            if (errno != 0) die("readdir /proc/self/fd");
            break;
        }
        if (e->d_name[0] == '.') continue;          /* "." і ".." */

        int fd = (int)strtol(e->d_name, NULL, 10);
        if (fd == own) continue;
        if (n < max) out[n++] = fd;
    }
    closedir(d);
    return n;
}
