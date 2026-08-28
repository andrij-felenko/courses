#include <atomic>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>

int futex_wait(std::atomic<int>* uaddr, int val) {
    return ::syscall(SYS_futex, uaddr, FUTEX_WAIT_PRIVATE, val, nullptr, nullptr, 0);
}

int futex_wake(std::atomic<int>* uaddr, int count) {
    return ::syscall(SYS_futex, uaddr, FUTEX_WAKE_PRIVATE, count, nullptr, nullptr, 0);
}
