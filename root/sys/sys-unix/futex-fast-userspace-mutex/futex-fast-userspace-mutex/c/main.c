#include <linux/futex.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdatomic.h>

int futex_wait(int *uaddr, int val) {
    return syscall(SYS_futex, uaddr, FUTEX_WAIT_PRIVATE, val, NULL, NULL, 0);
}

int futex_wake(int *uaddr, int count) {
    return syscall(SYS_futex, uaddr, FUTEX_WAKE_PRIVATE, count, NULL, NULL, 0);
}
