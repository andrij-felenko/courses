#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <spawn.h>
#include <sys/wait.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <string_view>
#include <system_error>
#include <vector>

extern char **environ;

#ifdef __GLIBC_PREREQ
# if __GLIBC_PREREQ(2, 34)
#  define HAVE_ADDCLOSEFROM 1
# endif
#endif

class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
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
};

class PosixSpawnFileActions {
    posix_spawn_file_actions_t fa_{};
public:
    PosixSpawnFileActions() {
        if (int err = ::posix_spawn_file_actions_init(&fa_))
            throw std::system_error(err, std::generic_category(), "init file actions");
    }
    ~PosixSpawnFileActions() noexcept { ::posix_spawn_file_actions_destroy(&fa_); }

    void add_dup2(int fd, int newfd) {
        if (int err = ::posix_spawn_file_actions_adddup2(&fa_, fd, newfd))
            throw std::system_error(err, std::generic_category(), "adddup2");
    }
    void add_open(int fd, const char* path, int flags, mode_t mode) {
        if (int err = ::posix_spawn_file_actions_addopen(&fa_, fd, path, flags, mode))
            throw std::system_error(err, std::generic_category(), "addopen");
    }
#ifdef HAVE_ADDCLOSEFROM
    void add_closefrom(int from) {
        if (int err = ::posix_spawn_file_actions_addclosefrom_np(&fa_, from))
            throw std::system_error(err, std::generic_category(), "addclosefrom");
    }
#endif
    const posix_spawn_file_actions_t* get() const noexcept { return &fa_; }
};

class PosixSpawnAttr {
    posix_spawnattr_t at_{};
public:
    PosixSpawnAttr() {
        if (int err = ::posix_spawnattr_init(&at_))
            throw std::system_error(err, std::generic_category(), "init spawn attr");
    }
    ~PosixSpawnAttr() noexcept { ::posix_spawnattr_destroy(&at_); }

    void set_sigmask(const sigset_t& mask) {
        if (int err = ::posix_spawnattr_setsigmask(&at_, &mask))
            throw std::system_error(err, std::generic_category(), "setsigmask");
    }
    void set_sigdefault(const sigset_t& mask) {
        if (int err = ::posix_spawnattr_setsigdefault(&at_, &mask))
            throw std::system_error(err, std::generic_category(), "setsigdefault");
    }
    void set_pgroup(pid_t pg) {
        if (int err = ::posix_spawnattr_setpgroup(&at_, pg))
            throw std::system_error(err, std::generic_category(), "setpgroup");
    }
    void set_flags(short flags) {
        if (int err = ::posix_spawnattr_setflags(&at_, flags))
            throw std::system_error(err, std::generic_category(), "setflags");
    }
    const posix_spawnattr_t* get() const noexcept { return &at_; }
};

static int run_sort(std::string_view lines, const char *out_path, int *status) {
    int pfd[2];
    if (::pipe2(pfd, O_CLOEXEC) == -1)
        return errno;
    UniqueFd read_end(pfd[0]);
    UniqueFd write_end(pfd[1]);

    try {
        PosixSpawnFileActions fa;
        fa.add_dup2(read_end.get(), STDIN_FILENO);
        fa.add_open(STDOUT_FILENO, out_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        fa.add_open(STDERR_FILENO, "/dev/null", O_WRONLY, 0);
#ifdef HAVE_ADDCLOSEFROM
        fa.add_closefrom(3);
#endif

        PosixSpawnAttr at;
        sigset_t empty, all;
        ::sigemptyset(&empty);
        ::sigfillset(&all);
        at.set_sigmask(empty);
        at.set_sigdefault(all);
        at.set_pgroup(0);
        at.set_flags(POSIX_SPAWN_SETSIGMASK | POSIX_SPAWN_SETSIGDEF | POSIX_SPAWN_SETPGROUP);

        std::vector<const char*> argv = { "sort", "-n", nullptr };
        pid_t pid = 0;
        int rc = ::posix_spawnp(&pid, "sort", fa.get(), at.get(),
                               const_cast<char* const*>(argv.data()), environ);
        if (rc != 0) return rc;

        read_end.reset();

        const char* ptr = lines.data();
        size_t remaining = lines.size();
        while (remaining > 0) {
            ssize_t written = ::write(write_end.get(), ptr, remaining);
            if (written < 0) {
                if (errno == EINTR) continue;
                break;
            }
            ptr += written;
            remaining -= written;
        }
        write_end.reset();

        return ::waitpid(pid, status, 0) == -1 ? errno : 0;
    } catch (const std::system_error& e) {
        return e.code().value();
    }
}

int main() {
    int status = 0;
    ::signal(SIGPIPE, SIG_IGN);

    int err = run_sort("30\n4\n100\n7\n", "sorted.txt", &status);
    if (err != 0) {
        std::cerr << "запустити не вдалося: " << std::strerror(err) << '\n';
        return 1;
    }
    if (WIFEXITED(status) && WEXITSTATUS(status) == 127) {
        std::cerr << "код 127: на цій системі так звітують про невдалий запуск\n";
    }
    return 0;
}
