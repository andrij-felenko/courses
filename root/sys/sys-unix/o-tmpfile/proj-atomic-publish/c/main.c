#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <libgen.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/xattr.h>
#include <unistd.h>

/* Один write не зобов'язаний узяти весь буфер. */
static int write_all(int fd, const void *buf, size_t len)
{
    const char *p = buf;
    while (len > 0) {
        ssize_t n = write(fd, p, len);
        if (n < 0) {
            if (errno == EINTR) continue;   /* сигнал, а не помилка */
            return -1;
        }
        p += n;
        len -= (size_t) n;
    }
    return 0;
}

/* Довговічність імені: сам каталог теж треба скинути на носій. */
static int fsync_dir(const char *dir)
{
    int dfd = open(dir, O_RDONLY | O_DIRECTORY);
    if (dfd < 0)
        return -1;
    if (fsync(dfd) < 0) {
        int e = errno;
        close(dfd);
        errno = e;
        return -1;
    }
    return close(dfd);
}

/* Спільна частина обох гілок: наповнити відкритий дескриптор і довести до пуття.
   uid/gid == -1 означає «не чіпати»; тоді CAP_CHOWN не потрібен. */
static int fill(int fd, const void *buf, size_t len,
                mode_t mode, uid_t uid, gid_t gid)
{
    if (write_all(fd, buf, len) < 0)
        return -1;
    if (fchown(fd, uid, gid) < 0)        /* спершу власник: він гасить біти set-uid/set-gid */
        return -1;
    if (fchmod(fd, mode) < 0)            /* аж потім права, і то точні: без umask */
        return -1;
    if (fsetxattr(fd, "user.app.generation", "7", 1, 0) < 0
        && errno != EOPNOTSUPP)          /* xattr вимкнено — не привід падати */
        return -1;
    return fsync(fd);                    /* уміст на носії — ДО того, як з'явиться ім'я */
}

/* Запасний шлях: файлова система не вміє O_TMPFILE. */
static int publish_via_rename(const char *dir, const char *target,
                              const void *buf, size_t len,
                              mode_t mode, uid_t uid, gid_t gid)
{
    char tmp[PATH_MAX];
    if (snprintf(tmp, sizeof tmp, "%s/.pub-XXXXXX", dir) >= (int) sizeof tmp) {
        errno = ENAMETOOLONG;
        return -1;
    }

    int fd = mkstemp(tmp);               /* із цієї миті ім'я видно в каталозі */
    if (fd < 0)
        return -1;

    int e;
    if (fill(fd, buf, len, mode, uid, gid) < 0) { e = errno; close(fd); goto fail; }
    if (close(fd) < 0)                          { e = errno;            goto fail; }

    /* RENAME_NOREPLACE тримає ту саму семантику, що linkat: зайняте ім'я — EEXIST. */
    if (renameat2(AT_FDCWD, tmp, AT_FDCWD, target, RENAME_NOREPLACE) < 0) {
        e = errno;
        if (e != EINVAL && e != ENOSYS)  /* ФС не знає прапорця / ядро не знає виклику */
            goto fail;
        if (rename(tmp, target) < 0)     /* тут семантика вже інша: мовчазна заміна */
            { e = errno; goto fail; }
    }
    return fsync_dir(dir);

fail:
    unlink(tmp);                         /* не лишати сміття під випадковим іменем */
    errno = e;
    return -1;
}

int publish(const char *target, const void *buf, size_t len,
            mode_t mode, uid_t uid, gid_t gid)
{
    char dirbuf[PATH_MAX];
    if (snprintf(dirbuf, sizeof dirbuf, "%s", target) >= (int) sizeof dirbuf) {
        errno = ENAMETOOLONG;
        return -1;
    }
    /* Каталог беремо з самої цілі: так inode напевно виникне на тій самій
       файловій системі, де йому потім давати ім'я. dirname() псує аргумент. */
    const char *dir = dirname(dirbuf);

    int fd = open(dir, O_TMPFILE | O_RDWR, mode);
    if (fd < 0) {
        if (errno == EOPNOTSUPP || errno == EISDIR)
            return publish_via_rename(dir, target, buf, len, mode, uid, gid);
        return -1;
    }

    int e;
    if (fill(fd, buf, len, mode, uid, gid) < 0) { e = errno; goto fail; }

    char proc[64];
    snprintf(proc, sizeof proc, "/proc/self/fd/%d", fd);
    if (linkat(AT_FDCWD, proc, AT_FDCWD, target, AT_SYMLINK_FOLLOW) < 0)
        { e = errno; goto fail; }        /* EEXIST — ім'я вже зайняте */

    if (fsync_dir(dir) < 0)              /* ім'я вже є: помилка тут — про довговічність */
        { e = errno; goto fail; }
    return close(fd);

fail:
    close(fd);                           /* до linkat() inode зникає сам, після нього ім'я вже лишається */
    errno = e;
    return -1;
}
