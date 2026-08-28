#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>
#include <spawn.h>
#include <sys/wait.h>
#include <signal.h>
#include <unistd.h>

class SpawnFileActionsRAII {
public:
    SpawnFileActionsRAII() {
        if (int err = posix_spawn_file_actions_init(&actions_); err != 0) {
            throw std::system_error(err, std::generic_category(), "posix_spawn_file_actions_init failed");
        }
    }
    ~SpawnFileActionsRAII() noexcept {
        posix_spawn_file_actions_destroy(&actions_);
    }
    SpawnFileActionsRAII(const SpawnFileActionsRAII&) = delete;
    SpawnFileActionsRAII& operator=(const SpawnFileActionsRAII&) = delete;

    int add_dup2(int fd, int new_fd) noexcept {
        return posix_spawn_file_actions_adddup2(&actions_, fd, new_fd);
    }
    int add_close(int fd) noexcept {
        return posix_spawn_file_actions_addclose(&actions_, fd);
    }
    const posix_spawn_file_actions_t* get() const noexcept { return &actions_; }

private:
    posix_spawn_file_actions_t actions_;
};

class SpawnAttributesRAII {
public:
    SpawnAttributesRAII() {
        if (int err = posix_spawnattr_init(&attr_); err != 0) {
            throw std::system_error(err, std::generic_category(), "posix_spawnattr_init failed");
        }
    }
    ~SpawnAttributesRAII() noexcept {
        posix_spawnattr_destroy(&attr_);
    }
    SpawnAttributesRAII(const SpawnAttributesRAII&) = delete;
    SpawnAttributesRAII& operator=(const SpawnAttributesRAII&) = delete;

    int set_sigdefault(const sigset_t& sigs) noexcept {
        return posix_spawnattr_setsigdefault(&attr_, &sigs);
    }
    int set_flags(short flags) noexcept {
        return posix_spawnattr_setflags(&attr_, flags);
    }
    int set_pgroup(pid_t pgroup) noexcept {
        return posix_spawnattr_setpgroup(&attr_, pgroup);
    }
    const posix_spawnattr_t* get() const noexcept { return &attr_; }

private:
    posix_spawnattr_t attr_;
};

std::expected<pid_t, std::error_code> spawn_grep_cpp(int input_pipe_fd, std::string_view pattern) {
    try {
        SpawnFileActionsRAII actions;
        SpawnAttributesRAII attr;

        if (int err = actions.add_dup2(input_pipe_fd, STDIN_FILENO); err != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(err)));
        }
        if (input_pipe_fd != STDIN_FILENO) {
            if (int err = actions.add_close(input_pipe_fd); err != 0) {
                return std::unexpected(std::make_error_code(static_cast<std::errc>(err)));
            }
        }

        sigset_t default_signals;
        sigemptyset(&default_signals);
        sigaddset(&default_signals, SIGPIPE);
        if (int err = attr.set_sigdefault(default_signals); err != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(err)));
        }

        short flags = POSIX_SPAWN_SETSIGDEF | POSIX_SPAWN_SETPGROUP;
        if (int err = attr.set_flags(flags); err != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(err)));
        }
        if (int err = attr.set_pgroup(0); err != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(err)));
        }

        std::string pattern_str(pattern);
        std::vector<char*> argv = {
            const_cast<char*>("grep"),
            pattern_str.data(),
            nullptr
        };

        pid_t pid = 0;
        extern char **environ;
        int status = posix_spawnp(&pid, "grep", actions.get(), attr.get(), argv.data(), environ);

        if (status != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(status)));
        }
        return pid;
    } catch (const std::system_error& e) {
        return std::unexpected(e.code());
    }
}
