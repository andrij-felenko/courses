/* two-counters.c — обидва лічильники файлу на власні очі.
   збірка: cc -O2 -Wall -Wextra -o two-counters two-counters.c
   запуск: ./two-counters /каталог/на/справжньому/диску            */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <unistd.h>

#define MIB     (1024ULL * 1024ULL)
#define PAYLOAD (64ULL * MIB)

static void die(const char *what) { perror(what); exit(1); }

/* Скільки байтів файлова система вважає вільними.
   f_bfree — сирі вільні блоки; f_bavail менший на резерв для root
   і на внутрішній резерв ext4, тож для досліду потрібен f_bfree.
   Одиниця лічильників блоків — f_frsize, а не f_bsize.           */
static unsigned long long free_bytes(const char *dir)
{
    struct statvfs vfs;
    if (statvfs(dir, &vfs) != 0) die("statvfs");
    return (unsigned long long) vfs.f_bfree * vfs.f_frsize;
}

static void report(int step, const char *stage, int fd, const char *dir)
{
    sync();                    /* інакше відлік залежить від того, що
                                  система ще не встигла записати */
    if (fd < 0) {
        printf("%d) ino=%-9s nlink=%-2s blocks=%-9s вільно=%6llu МіБ   %s\n",
               step, "-", "-", "-", free_bytes(dir) / MIB, stage);
        fflush(stdout);
        return;
    }

    struct stat st;
    if (fstat(fd, &st) != 0) die("fstat");
    printf("%d) ino=%-9llu nlink=%-2lu blocks=%-9llu вільно=%6llu МіБ   %s\n",
           step, (unsigned long long) st.st_ino, (unsigned long) st.st_nlink,
           (unsigned long long) st.st_blocks, free_bytes(dir) / MIB, stage);

    /* Який шлях ядро зараз приписує цьому дескрипторові. */
    char self[64], seen[4096];
    snprintf(self, sizeof self, "/proc/self/fd/%d", fd);
    ssize_t n = readlink(self, seen, sizeof seen - 1);
    if (n >= 0) { seen[n] = '\0'; printf("   %s → %s\n", self, seen); }
    fflush(stdout);
}

/* write() має право записати менше, ніж просили, — дописуємо решту. */
static void write_all(int fd, const char *p, size_t n)
{
    while (n > 0) {
        ssize_t k = write(fd, p, n);
        if (k < 0) { if (errno == EINTR) continue; die("write"); }
        p += k;
        n -= (size_t) k;
    }
}

int main(int argc, char **argv)
{
    const char *dir = (argc > 1) ? argv[1] : ".";
    char a[4096], b[4096];
    snprintf(a, sizeof a, "%s/counters-a.dat", dir);
    snprintf(b, sizeof b, "%s/counters-b.dat", dir);

    report(0, "до початку", -1, dir);

    int fd = open(a, O_RDWR | O_CREAT | O_EXCL, 0600);
    if (fd < 0) die(a);

    /* Псевдовипадкові байти, а не нулі й не однаковий символ: на ФС зі
       стисненням одноманітний вміст майже не займе місця — і міряти
       буде нічого.                                                  */
    static char buf[1 << 20];
    unsigned long long s = 88172645463325252ULL;      /* xorshift64 */
    for (size_t i = 0; i < sizeof buf; i++) {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        buf[i] = (char) s;
    }
    memcpy(buf, "TWO-COUNTERS", 12);                  /* впізнаваний початок */

    for (unsigned long long done = 0; done < PAYLOAD; done += sizeof buf)
        write_all(fd, buf, sizeof buf);
    if (fsync(fd) != 0) die("fsync");

    report(1, "записано 64 МіБ", fd, dir);

    if (link(a, b) != 0) die("link");
    report(2, "додано друге ім'я", fd, dir);

    if (unlink(a) != 0) die("unlink a");
    report(3, "знято перше ім'я", fd, dir);

    if (unlink(b) != 0) die("unlink b");
    report(4, "знято друге ім'я", fd, dir);

    char probe[13] = {0};
    if (pread(fd, probe, 12, 0) != 12) die("pread");
    printf("   через дескриптор читається: %.12s\n", probe);

    if (close(fd) != 0) die("close");
    report(5, "дескриптор закрито", -1, dir);
    return 0;
}
