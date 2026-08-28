#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/openat2.h>
#include <unistd.h>

struct open_how {
    __u64 flags;        /* Стандартні прапорці O_RDONLY, O_CREAT тощо */
    __u64 mode;         /* Вісімкові права доступу */
    __u64 resolve;      /* Прапорці сімейства RESOLVE_* */
};

int openat2(int dirfd, const char *pathname,
            struct open_how *how, size_t size);
