#define _GNU_SOURCE
#include <linux/openat2.h>   /* struct open_how, RESOLVE_* */
#include <sys/syscall.h>
#include <unistd.h>

/* оголошено в заголовку, наведено для довідки */
struct open_how {
    __u64 flags;     /* усе, що приймає open(): O_RDONLY, O_CREAT, O_CLOEXEC … */
    __u64 mode;      /* права нового файлу; поза O_CREAT/O_TMPFILE мусить бути 0 */
    __u64 resolve;   /* RESOLVE_* — керує самим обходом */
};

long syscall(SYS_openat2, int dirfd, const char *path,
             struct open_how *how, size_t size);
