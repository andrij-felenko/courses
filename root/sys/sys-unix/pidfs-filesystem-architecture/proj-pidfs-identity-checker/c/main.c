#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/types.h>

#ifndef SYS_pidfd_open
#define SYS_pidfd_open 434
#endif

#ifndef PIDFS_IOCTL_MAGIC
#define PIDFS_IOCTL_MAGIC 0xFF
#endif

#ifndef PIDFD_GET_NET_NAMESPACE
#define PIDFD_GET_NET_NAMESPACE _IO(PIDFS_IOCTL_MAGIC, 4)
#endif

#ifndef PIDFD_GET_INFO
struct pidfd_info {
    __u64 mask;
    __u64 cgroupid;
    __u32 pid;
    __u32 tgid;
    __u32 ppid;
    __u32 ruid;
    __u32 rgid;
    __u32 euid;
    __u32 egid;
    __u32 suid;
    __u32 sgid;
    __u32 fsuid;
    __u32 fsgid;
    __s32 exit_code;
};
#define PIDFD_GET_INFO _IOWR(PIDFS_IOCTL_MAGIC, 11, struct pidfd_info)
#define PIDFD_INFO_PID   (1U << 0)  /* pid, tgid, ppid */
#define PIDFD_INFO_CREDS (1U << 1)  /* ruid/rgid, euid/egid, suid/sgid, fsuid/fsgid */
#endif

static int open_pidfd(pid_t pid) {
    int fd = (int)syscall(SYS_pidfd_open, pid, 0U);
    if (fd < 0) {
        perror("pidfd_open failed");
    }
    return fd;
}

static int get_pidfs_stat(int pidfd, struct statx *stx) {
    memset(stx, 0, sizeof(*stx));
    if (statx(pidfd, "", AT_EMPTY_PATH, STATX_INO, stx) < 0) {
        perror("statx on pidfd failed");
        return -1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <PID_1> <PID_2>\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid1 = (pid_t)atoi(argv[1]);
    pid_t pid2 = (pid_t)atoi(argv[2]);

    int fd1 = open_pidfd(pid1);
    int fd2 = open_pidfd(pid2);
    if (fd1 < 0 || fd2 < 0) {
        if (fd1 >= 0) close(fd1);
        if (fd2 >= 0) close(fd2);
        return EXIT_FAILURE;
    }

    struct statx stx1, stx2;
    if (get_pidfs_stat(fd1, &stx1) < 0 || get_pidfs_stat(fd2, &stx2) < 0) {
        close(fd1);
        close(fd2);
        return EXIT_FAILURE;
    }

    printf("PID %d: dev=(%u,%u), ino=%llu\n", pid1,
           stx1.stx_dev_major, stx1.stx_dev_minor, (unsigned long long)stx1.stx_ino);
    printf("PID %d: dev=(%u,%u), ino=%llu\n", pid2,
           stx2.stx_dev_major, stx2.stx_dev_minor, (unsigned long long)stx2.stx_ino);

    if (stx1.stx_dev_major == stx2.stx_dev_major &&
        stx1.stx_dev_minor == stx2.stx_dev_minor &&
        stx1.stx_ino == stx2.stx_ino) {
        printf("РЕЗУЛЬТАТ: Дескриптори вказують на ОДИН І ТОЙ САМИЙ процес!\n");
    } else {
        printf("РЕЗУЛЬТАТ: Це РІЗНІ процеси.\n");
    }

    /* Отримання Network Namespace першого процесу */
    int netns_fd = ioctl(fd1, PIDFD_GET_NET_NAMESPACE, 0);
    if (netns_fd >= 0) {
        printf("Успішно отримано netns fd=%d для PID %d\n", netns_fd, pid1);
        close(netns_fd);
    } else {
        printf("Отримання netns не вдалося: %s\n", strerror(errno));
    }

    /* Отримання метаданих через PIDFD_GET_INFO */
    struct pidfd_info info;
    memset(&info, 0, sizeof(info));
    info.mask = PIDFD_INFO_PID | PIDFD_INFO_CREDS;
    if (ioctl(fd1, PIDFD_GET_INFO, &info) >= 0) {
        printf("Метадані PIDFD_GET_INFO: PID=%u, PPID=%u, EUID=%u, EGID=%u\n",
               info.pid, info.ppid, info.euid, info.egid);
    } else {
        printf("PIDFD_GET_INFO не підтримується або завершився з помилкою: %s\n", strerror(errno));
    }

    close(fd1);
    close(fd2);
    return EXIT_SUCCESS;
}
