#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* type: F_RDLCK / F_WRLCK / F_UNLCK; len = 0 — до кінця файлу.
   Повертає 0, або -1 з errno. */
static int ofd_lock(int fd, short type, off_t start, off_t len, int wait)
{
    struct flock fl;
    memset(&fl, 0, sizeof fl);        /* l_pid = 0 — умова для F_OFD_* */
    fl.l_type   = type;
    fl.l_whence = SEEK_SET;
    fl.l_start  = start;
    fl.l_len    = len;

    int op = wait ? F_OFD_SETLKW : F_OFD_SETLK;
    int r;
    do {
        r = fcntl(fd, op, &fl);
    } while (r == -1 && errno == EINTR);   /* чужий обробник міг бути без SA_RESTART */
    return r;
}

int main(void)
{
    int fd = open("data.bin", O_RDWR | O_CREAT | O_CLOEXEC, 0644);
    if (fd < 0) { perror("open"); return 1; }

    if (ofd_lock(fd, F_WRLCK, 0, 0, 0) == -1) {
        if (errno == EAGAIN || errno == EACCES)
            fputs("діапазон тримає інший опис\n", stderr);
        else if (errno == EINVAL)
            fputs("ядро без OFD-замків (до 3.15)\n", stderr);
        else
            perror("F_OFD_SETLK");
        return 1;
    }

    /* розвідка тим самим описом: власний замок конфліктом не рахується */
    struct flock probe;
    memset(&probe, 0, sizeof probe);
    probe.l_type   = F_WRLCK;
    probe.l_whence = SEEK_SET;        /* l_len = 0 — увесь файл */
    if (fcntl(fd, F_OFD_GETLK, &probe) == 0)
        printf("F_OFD_GETLK: l_type=%d l_pid=%d\n", probe.l_type, probe.l_pid);

    pause();                          /* тримаємо замок, доки не вб'ють */
    return 0;
}
