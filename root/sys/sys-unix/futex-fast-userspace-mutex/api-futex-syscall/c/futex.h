#include <linux/futex.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <time.h>

// Класичний системний виклик futex (номер виклику SYS_futex)
long syscall(SYS_futex, uint32_t *uaddr, int op, uint32_t val,
             const struct timespec *timeout, uint32_t *uaddr2, uint32_t val3);

// Векторний системний виклик futex2 (номер виклику SYS_futex_waitv)
long syscall(SYS_futex_waitv, struct futex_waitv *waiters, unsigned int nr_futexes,
             unsigned int flags, struct timespec *timeout, clockid_t clockid);
