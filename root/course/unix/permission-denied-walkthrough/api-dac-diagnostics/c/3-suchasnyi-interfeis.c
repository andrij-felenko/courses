#include <fcntl.h>
#include <linux/openat2.h>
#include <sys/syscall.h>

struct open_how {
    __u64 flags;        /* Прапорці відкриття (O_RDONLY, O_CREAT, O_CLOEXEC тощо) */
    __u64 mode;         /* Права створення файлу (0644) */
    __u64 resolve;      /* Прапорці поведінки розбору шляху (RESOLVE_*) */
};

int openat2(int dirfd, const char *pathname, struct open_how *how, size_t size);
