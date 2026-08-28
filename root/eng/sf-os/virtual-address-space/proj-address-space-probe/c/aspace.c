/* aspace.c — прогулянка власним адресним простором.
 * gcc -O2 -o aspace aspace.c        запуск: ./aspace
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <setjmp.h>
#include <signal.h>
#include <sys/mman.h>

#define MIB (1024UL * 1024)
static unsigned long PAGE;

/* Два перші числа з /proc/self/statm — VmSize і VmRSS, обидва в СТОРІНКАХ. */
static void show(const char *what)
{
    char buf[128];
    unsigned long vsz = 0, rss = 0;
    int fd = open("/proc/self/statm", O_RDONLY);
    if (fd >= 0) {
        ssize_t n = read(fd, buf, sizeof buf - 1);
        close(fd);
        if (n > 0) { buf[n] = '\0'; sscanf(buf, "%lu %lu", &vsz, &rss); }
    }
    /* мітку друкуємо ОСТАННЬОЮ: ширину поля лічать у байтах, а кирилиця
       в UTF-8 займає по два — вирівняти можна лише те, що ліворуч від неї */
    printf("VSZ %8.1f МіБ   RSS %8.2f МіБ (%6lu стор.)   %s\n",
           (double) vsz * PAGE / MIB, (double) rss * PAGE / MIB, rss, what);
}

/* Ті рядки /proc/self/maps, що описують саме нашу ділянку. */
static void maps(const char *what, char *lo, char *hi)
{
    printf("--- /proc/self/maps, %s\n", what);
    FILE *f = fopen("/proc/self/maps", "r");
    if (!f) return;
    char line[512];
    unsigned long a, b;
    while (fgets(line, sizeof line, f))
        if (sscanf(line, "%lx-%lx", &a, &b) == 2 &&
            a < (unsigned long) hi && b > (unsigned long) lo)
            fputs(line, stdout);
    fclose(f);
}
