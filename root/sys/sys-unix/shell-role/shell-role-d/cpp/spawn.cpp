#include "spawn.hpp"

#include <spawn.h>

#include <csignal>
#include <stdexcept>
#include <system_error>

extern char** environ;

namespace {

void check(int err, const char* what)
{
    if (err != 0) {
        throw std::system_error(err, std::generic_category(), what);
    }
}

// Обидві структури posix_spawn вимагають парного destroy — і жоден
// throw посеред налаштування більше не може його пропустити.
class FileActions {
public:
    FileActions() { check(::posix_spawn_file_actions_init(&actions_), "file_actions_init"); }
    ~FileActions() { ::posix_spawn_file_actions_destroy(&actions_); }

    FileActions(const FileActions&) = delete;
    FileActions& operator=(const FileActions&) = delete;

    void dup2(int from, int to) { check(::posix_spawn_file_actions_adddup2(&actions_, from, to), "adddup2"); }
    void close(int fd) { check(::posix_spawn_file_actions_addclose(&actions_, fd), "addclose"); }

    [[nodiscard]] ::posix_spawn_file_actions_t* get() noexcept { return &actions_; }

private:
    ::posix_spawn_file_actions_t actions_{};
};

class SpawnAttr {
public:
    SpawnAttr() { check(::posix_spawnattr_init(&attr_), "spawnattr_init"); }
    ~SpawnAttr() { ::posix_spawnattr_destroy(&attr_); }

    SpawnAttr(const SpawnAttr&) = delete;
    SpawnAttr& operator=(const SpawnAttr&) = delete;

    // Групу процесів виставляє ядро між clone() та execve():
    // вікна гонки, як із ручним setpgid(), тут просто немає.
    void set_pgroup(::pid_t pgid)
    {
        check(::posix_spawnattr_setpgroup(&attr_, pgid), "setpgroup");
        flags_ |= POSIX_SPAWN_SETPGROUP;
    }

    // Оболонка ігнорувала термінальні сигнали — програмі потрібна типова дія.
    void reset_signals()
    {
        ::sigset_t to_default{};
        ::sigset_t empty{};
        ::sigemptyset(&empty);
        ::sigemptyset(&to_default);
        for (int sig : { SIGINT, SIGQUIT, SIGTSTP, SIGTTIN, SIGTTOU, SIGCHLD }) {
            ::sigaddset(&to_default, sig);
        }
        check(::posix_spawnattr_setsigdefault(&attr_, &to_default), "setsigdefault");
        check(::posix_spawnattr_setsigmask(&attr_, &empty), "setsigmask");
        flags_ |= POSIX_SPAWN_SETSIGDEF | POSIX_SPAWN_SETSIGMASK;
    }

    [[nodiscard]] ::posix_spawnattr_t* get()
    {
        check(::posix_spawnattr_setflags(&attr_, flags_), "setflags");
        return &attr_;
    }

private:
    ::posix_spawnattr_t attr_{};
    short flags_ = 0;
};

}  // namespace

::pid_t spawn_stage(const std::string& path,
                    std::span<const std::string> args,
                    const StageIo& io)
{
    if (args.empty()) {
        throw std::invalid_argument("порожня ланка конвеєра");
    }

    FileActions actions;
    if (io.in_fd != STDIN_FILENO) {
        actions.dup2(io.in_fd, STDIN_FILENO);
    }
    if (io.out_fd != STDOUT_FILENO) {
        actions.dup2(io.out_fd, STDOUT_FILENO);
    }
    // Копії дескрипторів каналу нащадку не потрібні: зайвий відкритий
    // кінець запису означав би, що читач ланки не побачить EOF.
    for (int fd : io.close_fds) {
        if (fd > STDERR_FILENO) {
            actions.close(fd);
        }
    }

    SpawnAttr attr;
    attr.set_pgroup(io.pgid);
    attr.reset_signals();

    std::vector<char*> argv;
    argv.reserve(args.size() + 1);
    for (const auto& a : args) {
        argv.push_back(const_cast<char*>(a.c_str()));
    }
    argv.push_back(nullptr);

    ::pid_t pid = -1;
    // posix_spawnp повертає код помилки значенням, а не через errno.
    if (const int err = ::posix_spawnp(&pid, path.c_str(), actions.get(), attr.get(),
                                       argv.data(), environ);
        err != 0) {
        throw std::system_error(err, std::generic_category(), "posix_spawnp: " + path);
    }
    return pid;
}
