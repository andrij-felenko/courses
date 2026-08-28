#include <linux/openat2.h>
#include <sys/syscall.h>
#include <unistd.h>

struct open_how {
    __u64 flags;      /* ті самі O_*, що в openat(2) */
    __u64 mode;       /* лише біти 07777 */
    __u64 resolve;    /* маска RESOLVE_* */
};

long syscall(SYS_openat2, int dirfd, const char *pathname,
             struct open_how *how, size_t size);
