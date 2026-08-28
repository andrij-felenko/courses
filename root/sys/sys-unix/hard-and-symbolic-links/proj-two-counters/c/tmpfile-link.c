/* tmpfile-link.c — файл, якому ім'я дають наприкінці.
   збірка: cc -O2 -Wall -Wextra -o tmpfile-link tmpfile-link.c      */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static void die(const char *what) { perror(what); exit(1); }

static void show(int step, const char *stage, int fd)
{
    struct stat st;
    if (fstat(fd, &st) != 0) die("fstat");

    char self[64], seen[4096];
    snprintf(self, sizeof self, "/proc/self/fd/%d", fd);
    ssize_t n = readlink(self, seen, sizeof seen - 1);
    if (n < 0) die("readlink");
    seen[n] = '\0';

    printf("%d) ino=%-9llu nlink=%-2lu %s\n   %s → %s\n",
           step, (unsigned long long) st.st_ino,
           (unsigned long) st.st_nlink, stage, self, seen);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    const char *dir = (argc > 1) ? argv[1] : ".";
    char final_name[4096], self[64];
    snprintf(final_name, sizeof final_name, "%s/result.dat", dir);

    /* Перший аргумент — КАТАЛОГ, а не ім'я файлу: ми просимо inode
       «десь у цій файловій системі», не називаючи його.            */
    int fd = open(dir, O_TMPFILE | O_RDWR, 0600);
    if (fd < 0) {
        if (errno == EOPNOTSUPP || errno == EISDIR)
            fprintf(stderr, "O_TMPFILE тут недоступний (%s): потрібні "
                            "новіше ядро або інша ФС\n", strerror(errno));
        else
            perror("open O_TMPFILE");
        return 1;
    }

    show(1, "щойно народжений", fd);

    const char payload[] = "порахований результат\n";
    if (write(fd, payload, sizeof payload - 1) != (ssize_t) (sizeof payload - 1))
        die("write");
    if (fsync(fd) != 0) die("fsync");      /* дані на носій — ДО імені */

    show(2, "дані записано, імені все ще немає", fd);

    /* AT_SYMLINK_FOLLOW обов'язковий: /proc/self/fd/N — символьне
       посилання, і без прапорця linkat цілив би в сам вузол у procfs,
       а це інша файлова система — дістали б EXDEV.                  */
    snprintf(self, sizeof self, "/proc/self/fd/%d", fd);
    if (linkat(AT_FDCWD, self, AT_FDCWD, final_name, AT_SYMLINK_FOLLOW) != 0)
        die("linkat");

    show(3, "ім'я з'явилося", fd);

    /* Щоб ІМ'Я пережило вимкнення живлення, синхронізуємо каталог. */
    int dfd = open(dir, O_RDONLY | O_DIRECTORY);
    if (dfd < 0) die("open dir");
    if (fsync(dfd) != 0) die("fsync dir");
    close(dfd);
    close(fd);

    printf("готовий файл: %s\n", final_name);
    return 0;
}
