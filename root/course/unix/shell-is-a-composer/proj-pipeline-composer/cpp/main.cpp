#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <span>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <termios.h>

// Безпечна RAII-обгортка над системним файловим дескриптором
class UniqueFd {
    int fd_ = -1;
public:
    UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

struct PipePair {
    UniqueFd read_end;
    UniqueFd write_end;

    static std::expected<PipePair, std::error_code> create() {
        int fds[2];
        if (::pipe2(fds, O_CLOEXEC) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return PipePair{UniqueFd(fds[0]), UniqueFd(fds[1])};
    }
};

struct Command {
    std::vector<std::string> args;
};

struct PipelineResult {
    int last_status{0};
    int pipefail_status{0};
    std::vector<int> all_statuses;
};

class PipelineComposer {
public:
    static std::expected<PipelineResult, std::error_code> execute(std::span<const Command> commands) {
        if (commands.empty()) {
            return PipelineResult{};
        }

        const size_t n = commands.size();
        std::vector<PipePair> pipes;
        pipes.reserve(n > 1 ? n - 1 : 0);

        for (size_t i = 0; i + 1 < n; ++i) {
            auto pipe_res = PipePair::create();
            if (!pipe_res) {
                return std::unexpected(pipe_res.error());
            }
            pipes.push_back(std::move(*pipe_res));
        }

        std::vector<pid_t> pids(n, 0);
        pid_t pgid = 0;
        const bool interactive = ::isatty(STDIN_FILENO) != 0;
        const pid_t shell_pgid = ::getpgrp();

        for (size_t i = 0; i < n; ++i) {
            pid_t pid = ::fork();
            if (pid < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            if (pid == 0) {
                pid_t cur_pid = ::getpid();
                pid_t target_pgid = (i == 0) ? cur_pid : pgid;
                ::setpgid(0, target_pgid);

                if (i > 0) {
                    if (::dup2(pipes[i - 1].read_end.get(), STDIN_FILENO) == -1) {
                        ::_exit(127);
                    }
                }

                if (i + 1 < n) {
                    if (::dup2(pipes[i].write_end.get(), STDOUT_FILENO) == -1) {
                        ::_exit(127);
                    }
                }

                for (auto& p : pipes) {
                    p.read_end.reset();
                    p.write_end.reset();
                }

                std::vector<char*> raw_args;
                raw_args.reserve(commands[i].args.size() + 1);
                for (const auto& arg : commands[i].args) {
                    raw_args.push_back(const_cast<char*>(arg.c_str()));
                }
                raw_args.push_back(nullptr);

                ::execvp(raw_args[0], raw_args.data());
                ::_exit(127);
            }

            pids[i] = pid;
            if (i == 0) {
                pgid = pid;
            }
            ::setpgid(pid, pgid);
        }

        pipes.clear();

        if (interactive && pgid > 0) {
            ::tcsetpgrp(STDIN_FILENO, pgid);
        }

        PipelineResult result;
        result.all_statuses.resize(n, 0);
        int pipefail_code = 0;

        for (size_t i = 0; i < n; ++i) {
            int wstatus = 0;
            while (::waitpid(pids[i], &wstatus, 0) == -1) {
                if (errno == EINTR) continue;
                break;
            }

            int code = 0;
            if (WIFEXITED(wstatus)) {
                code = WEXITSTATUS(wstatus);
            } else if (WIFSIGNALED(wstatus)) {
                code = 128 + WTERMSIG(wstatus);
            }

            result.all_statuses[i] = code;
            if (code != 0) {
                pipefail_code = code;
            }
        }

        if (interactive) {
            ::tcsetpgrp(STDIN_FILENO, shell_pgid);
        }

        result.last_status = result.all_statuses.back();
        result.pipefail_status = pipefail_code;
        return result;
    }
};
