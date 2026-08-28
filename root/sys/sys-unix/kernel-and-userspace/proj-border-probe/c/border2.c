/* border2.c — одна погана адреса з трьох боків.  gcc -O2 -o border2 border2.c */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>

static void probe(const char *what, int fd, const void *p, size_t n)
{
    errno = 0;
    ssize_t r = write(fd, p, n);
    /* мітку друкуємо ОСТАННЬОЮ: ширина поля рахує байти, а кирилиця в UTF-8
       займає по два — вирівняти можна лише те, що ліворуч від неї */
    printf("r=%4zd  errno=%2d %-11s  %s\n",
           r, errno, r < 0 ? strerror(errno) : "-", what);
}

int main(void)
{
    char *nopage  = (char *) 0x10L;       /* адреса з діапазону користувача, сторінки немає */
    char *notours = (char *) -4096L;      /* адреса взагалі не з нашого боку межі          */

    int null = open("/dev/null", O_WRONLY);
    int file = open("border2.out", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (null < 0 || file < 0) { perror("open"); return 1; }

    probe("нема сторінки -> /dev/null, 16 Б", null, nopage,  16);
    probe("нема сторінки -> файл, 16 Б",      file, nopage,  16);
    probe("нема сторінки -> файл, 0 Б",       file, nopage,   0);
    probe("не наш бік -> /dev/null, 16 Б",    null, notours, 16);

    fflush(stdout);                       /* ← приберіть цей рядок і перечитайте пастки */

    volatile char *self = (volatile char *) nopage;
    printf("а тепер розіменуємо самі: %d\n", (int) *self);
    return 0;
}
