#define _GNU_SOURCE
#include <errno.h>
#include <linux/sched.h>
#include <linux/types.h>
#include <signal.h>
#include <stdint.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
#include <iostream>
#include <system_error>

class UniquePidFd {
    int fd_{-1};
public:
    constexpr UniquePidFd() noexcept = default;
    explicit UniquePidFd(int fd) noexcept : fd_(fd) {}
    ~UniquePidFd() { reset(); }

    UniquePidFd(const UniquePidFd&) = delete;
    UniquePidFd& operator=(const UniquePidFd&) = delete;

    UniquePidFd(UniquePidFd&& other) noexcept : fd_(other.release()) {}
    UniquePidFd& operator=(UniquePidFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) ::close(fd_);
        fd_ = new_fd;
    }
    [[nodiscard]] int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] int* ptr() noexcept { return &fd_; }
};

static long spawn_task(int *pidfd_out) {
    struct clone_args args{};
    args.flags = CLONE_PIDFD | CLONE_CLEAR_SIGHAND;
    args.pidfd = static_cast<__u64>(reinterpret_cast<uintptr_t>(pidfd_out));
    args.exit_signal = SIGCHLD;

    long pid = ::syscall(SYS_clone3, &args, sizeof(args));
    if (pid >= 0 || (errno != ENOSYS && errno != EINVAL && errno != E2BIG)) {
        return pid;
    }

    return ::syscall(SYS_clone, static_cast<unsigned long>(CLONE_PIDFD | SIGCHLD),
                     nullptr, pidfd_out, nullptr, 0UL);
}

int main() {
    UniquePidFd pidfd;
    long pid = spawn_task(pidfd.ptr());
    if (pid < 0) {
        std::cerr << "clone помилка: " << std::generic_category().message(errno) << '\n';
        return 1;
    }

    if (pid == 0) {
        ::execlp("id", "id", static_cast<char*>(nullptr));
        ::_exit(127);
    }

    siginfo_t info{};
    if (::waitid(P_PIDFD, static_cast<id_t>(pidfd.get()), &info, WEXITED) == 0) {
        std::cout << "дитина " << info.si_pid << " вийшла з кодом " << info.si_status << '\n';
    }
    return 0;
}
