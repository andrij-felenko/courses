/* durable-replace.c — заміна вмісту файлу, що переживає збій.
   збірка: cc -O2 -Wall -Wextra -o durable-replace durable-replace.c */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

/* write має право взяти менше, ніж просили, і має право повернутися
   ні з чим, якщо його перервав сигнал. Обидва випадки — не помилки. */
static int write_all(int fd, const void *buf, size_t len)
{
    const char *p = (const char *) buf;
    while (len > 0) {
        ssize_t n = write(fd, p, len);
        if (n < 0) {
            if (errno == EINTR) continue;
            return errno;
        }
        if (n == 0) return EIO;    /* для звичайного файлу не буває;
                                      краще помилка, ніж вічний цикл */
        p   += (size_t) n;
        len -= (size_t) n;
    }
    return 0;
}

/* Єдиний errno, після якого fsync можна кликати вдруге, — EINTR.
   Будь-який інший означає, що дані втрачено, і повторний виклик
   поверне облудний нуль: скидати вже нічого.                      */
static int fsync_checked(int fd)
{
    while (fsync(fd) != 0)
        if (errno != EINTR) return errno;
    return 0;
}

/* Замінити вміст файлу name у каталозі dir на buf/len.
   Повертає 0 або номер помилки (значення з errno.h).              */
int durable_replace(const char *dir, const char *name,
                    const void *buf, size_t len)
{
    int dfd = -1, fd = -1, rc = 0, have_tmp = 0;
    char tmp[NAME_MAX + 1];
    struct stat st;

    dfd = open(dir, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (dfd < 0) return errno;

    /* Тимчасове ім'я — у ЦЬОМУ ж каталозі. Крапка на початку ховає його
       від ls, номер процесу з лічильником розводять два одночасні
       виклики, а O_EXCL робить перевірку «чи вільне ім'я» неподільною. */
    for (unsigned attempt = 0; ; attempt++) {
        int k = snprintf(tmp, sizeof tmp, ".%s.%ld.%u.tmp",
                         name, (long) getpid(), attempt);
        if (k < 0 || (size_t) k >= sizeof tmp) { rc = ENAMETOOLONG; goto out; }

        fd = openat(dfd, tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
        if (fd >= 0) break;
        if (errno != EEXIST || attempt >= 1000) { rc = errno; goto out; }
    }
    have_tmp = 1;

    /* Права — від старого файлу. Свіжостворений має 0600 за вирахуванням
       umask, і після заміни конфіг раптово стає нечитним для служби.    */
    if (fstatat(dfd, name, &st, 0) == 0) {
        if (fchmod(fd, st.st_mode & 07777) != 0) { rc = errno; goto out; }
    } else if (errno != ENOENT) {
        rc = errno; goto out;
    }

    if ((rc = write_all(fd, buf, len)) != 0) goto out;

    /* Найдорожчий рядок функції: тут програма справді чекає на пристрій. */
    if ((rc = fsync_checked(fd)) != 0) goto out;

    /* close теж уміє провалитися — на мережевій файловій системі й на
       системах із відкладеним виділенням саме тут спливає ENOSPC.      */
    if (close(fd) != 0) { fd = -1; rc = errno; goto out; }
    fd = -1;

    /* Підміна імені. Неподільна: чужий процес бачить або старий файл,
       або новий, і ніколи — відсутність файлу.                        */
    if (renameat(dfd, tmp, dfd, name) != 0) { rc = errno; goto out; }
    have_tmp = 0;                       /* тимчасового імені більше нема */

    /* Запис у каталозі — теж дані в кеші сторінок, і власного дескриптора
       він не має. Просимо про його довговічність через сам каталог.     */
    rc = fsync_checked(dfd);

out:
    if (fd >= 0) close(fd);
    if (have_tmp) unlinkat(dfd, tmp, 0);
    if (dfd >= 0) close(dfd);
    return rc;         /* errno тут уже затоптаний прибиранням — тому rc */
}

int main(int argc, char **argv)
{
    if (argc < 4) {
        fprintf(stderr, "вжиток: %s <каталог> <ім'я> <рядок>\n", argv[0]);
        return 2;
    }
    int rc = durable_replace(argv[1], argv[2], argv[3], strlen(argv[3]));
    if (rc != 0) {
        fprintf(stderr, "заміна не вдалася: %s\n", strerror(rc));
        return 1;
    }
    return 0;
}
