#include <linux/ioprio.h>
#include <sys/syscall.h>
#include <unistd.h>

static inline int ioprio_set(int which, int who, int ioprio) {
    return syscall(SYS_ioprio_set, which, who, ioprio);
}
static inline int ioprio_get(int which, int who) {
    return syscall(SYS_ioprio_get, which, who);
}
