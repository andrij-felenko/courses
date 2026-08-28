#define _GNU_SOURCE
#include <stdio.h>
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>

/* Не вірити на слово: спитати ядро, який режим у вже відкритого об'єкта. */
static void show(const char *what, int fd)
{
    struct stat st;
    if (fstat(fd, &st) != 0) { perror("fstat"); return; }
    printf("%s: %04o\n", what, (unsigned) (st.st_mode & 07777));
}

/* Каталог: створюємо не ширшим за ціль, розширюємо вже за дескриптором. */
static int make_dir_exact(const char *path, mode_t want)
{
    if (mkdir(path, 0700) != 0) { perror("mkdir"); return -1; }

    /* O_NOFOLLOW: якщо між mkdir і open ім'я підмінили посиланням — падаємо. */
    int dfd = open(path, O_RDONLY | O_DIRECTORY | O_NOFOLLOW);
    if (dfd < 0) { perror("open dir"); return -1; }

    struct stat st;
    if (fstat(dfd, &st) != 0) { perror("fstat dir"); close(dfd); return -1; }

    /* setgid, успадкований від батьківського каталогу, зберігаємо. */
    if (fchmod(dfd, want | (st.st_mode & S_ISGID)) != 0) {
        perror("fchmod dir"); close(dfd); return -1;
    }
    show("каталог", dfd);
    return dfd;
}

/* Файл усередині цього каталогу — за дескриптором каталогу, не за шляхом. */
static int make_file_exact(int dfd, const char *name, mode_t want)
{
    int fd = openat(dfd, name, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, want);
    if (fd < 0) { perror("openat"); return -1; }
    if (fchmod(fd, want) != 0) { perror("fchmod"); close(fd); return -1; }
    show("ключ", fd);
    return fd;
}

int main(void)
{
    int dfd = make_dir_exact("vault", 0750);
    if (dfd < 0) return 1;

    int fd = make_file_exact(dfd, "key.pem", 0600);
    if (fd < 0) return 1;

    char tmpl[] = "/tmp/vault-XXXXXX";
    int tfd = mkstemp(tmpl);
    if (tfd < 0) { perror("mkstemp"); return 1; }
    if (fchmod(tfd, 0600) != 0) { perror("fchmod tmp"); return 1; }
    show("тимчасовий", tfd);

    close(fd); close(dfd); close(tfd);
    unlink(tmpl);
    return 0;
}
