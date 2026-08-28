/* share.c — два процеси на одному кадрі й розхід кадрів на першому записі */
#include "pagemap.h"
#include <string.h>
#include <sys/mman.h>
#include <sys/wait.h>

/* Відкриваємо pagemap на кожен звіт: описувач прив'язаний до простору того,
   хто його відкрив, тож успадкований від батька дивився б у батьків простір. */
static void report(const char *who, const void *addr)
{
    int fd = pm_open();
    uint64_t w;
    if (pm_read(fd, addr, &w) == 0)
        pm_print(who, addr, w);
    close(fd);
}

/* Перед тим як пустити іншого, виливаємо свої рядки: інакше вивід перемішається,
   а після fork ще й загубиться — _exit не зливає буфери stdio. */
static void notify(int fd)
{
    fflush(stdout);
    if (write(fd, "x", 1) != 1) { perror("write"); exit(1); }
}

static void expect(int fd)
{
    char c;
    if (read(fd, &c, 1) != 1) { perror("read"); exit(1); }
}

int main(void)
{
    long ps = pm_page_size();
    int  c2p[2], p2c[2];

    char *p = mmap(NULL, ps, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); exit(1); }
    strcpy(p, "спільний вміст");          /* дотик: кадр з'явився */

    if (pipe(c2p) < 0 || pipe(p2c) < 0) { perror("pipe"); exit(1); }

    report("батько до fork", p);
    fflush(stdout);      /* інакше дитина успадкує невилитий буфер і повторить рядок */

    pid_t pid = fork();
    if (pid < 0) { perror("fork"); exit(1); }

    if (pid == 0) {
        report("дитина одразу після fork", p);
        notify(c2p[1]);
        expect(p2c[0]);

        strcpy(p, "змінено дитиною");     /* ← ось тут кадр і копіюється */

        report("дитина після запису", p);
        printf("дитина бачить: «%s»\n", p);
        notify(c2p[1]);
        expect(p2c[0]);
        _exit(0);
    }

    expect(c2p[0]);
    report("батько одразу після fork", p);
    notify(p2c[1]);

    expect(c2p[0]);
    report("батько після запису дитини", p);
    printf("батько бачить: «%s»\n", p);
    notify(p2c[1]);

    wait(NULL);
    return 0;
}
