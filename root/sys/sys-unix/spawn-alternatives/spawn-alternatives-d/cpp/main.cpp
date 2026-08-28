#include <spawn.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/wait.h>
#include <iostream>
#include <system_error>
#include <vector>

extern char **environ;

class PosixSpawnFileActions {
    posix_spawn_file_actions_t actions_{};
public:
    PosixSpawnFileActions() {
        if (int err = posix_spawn_file_actions_init(&actions_)) {
            throw std::system_error(err, std::generic_category(), "init file actions");
        }
    }
    ~PosixSpawnFileActions() noexcept {
        posix_spawn_file_actions_destroy(&actions_);
    }
    PosixSpawnFileActions(const PosixSpawnFileActions&) = delete;
    PosixSpawnFileActions& operator=(const PosixSpawnFileActions&) = delete;

    void add_open(int fd, const char* path, int oflag, mode_t mode) {
        if (int err = posix_spawn_file_actions_addopen(&actions_, fd, path, oflag, mode)) {
            throw std::system_error(err, std::generic_category(), "addopen");
        }
    }
    void add_dup2(int fd, int newfd) {
        if (int err = posix_spawn_file_actions_adddup2(&actions_, fd, newfd)) {
            throw std::system_error(err, std::generic_category(), "adddup2");
        }
    }
    const posix_spawn_file_actions_t* get() const noexcept { return &actions_; }
};

class PosixSpawnAttr {
    posix_spawnattr_t attr_{};
public:
    PosixSpawnAttr() {
        if (int err = posix_spawnattr_init(&attr_)) {
            throw std::system_error(err, std::generic_category(), "init attr");
        }
    }
    ~PosixSpawnAttr() noexcept {
        posix_spawnattr_destroy(&attr_);
    }
    PosixSpawnAttr(const PosixSpawnAttr&) = delete;
    PosixSpawnAttr& operator=(const PosixSpawnAttr&) = delete;

    void set_sigmask(const sigset_t& mask) {
        if (int err = posix_spawnattr_setsigmask(&attr_, &mask)) {
            throw std::system_error(err, std::generic_category(), "setsigmask");
        }
    }
    void set_flags(short flags) {
        if (int err = posix_spawnattr_setflags(&attr_, flags)) {
            throw std::system_error(err, std::generic_category(), "setflags");
        }
    }
    const posix_spawnattr_t* get() const noexcept { return &attr_; }
};

int main() {
    try {
        PosixSpawnFileActions actions;
        actions.add_open(STDOUT_FILENO, "out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        actions.add_dup2(STDOUT_FILENO, STDERR_FILENO);

        PosixSpawnAttr attr;
        sigset_t none;
        sigemptyset(&none);
        attr.set_sigmask(none);
        attr.set_flags(POSIX_SPAWN_SETSIGMASK);

        std::vector<const char*> argv = { "ls", "-l", nullptr };
        pid_t pid = 0;
        int rc = posix_spawnp(&pid, "ls", actions.get(), attr.get(),
                               const_cast<char* const*>(argv.data()), environ);

        if (rc != 0) {
            throw std::system_error(rc, std::generic_category(), "posix_spawnp");
        }

        int status = 0;
        ::waitpid(pid, &status, 0);
    } catch (const std::exception& e) {
        std::cerr << "запустити не вдалося: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
