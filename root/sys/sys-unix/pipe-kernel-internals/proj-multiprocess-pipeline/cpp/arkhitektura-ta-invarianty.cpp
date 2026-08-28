#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/types.h>

// RAII-обгортка над сирим файловим дескриптором
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
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

private:
    int fd_;
};

struct Stage {
    std::vector<std::string> args;
};

// Виконання ланцюжка процесів із RAII-керуванням дескрипторами
int execute_pipeline(const std::vector<Stage>& stages) {
    if (stages.empty()) return 0;
    const size_t n = stages.size();

    if (n == 1) {
        pid_t pid = ::fork();
        if (pid < 0) throw std::system_error(errno, std::generic_category(), "fork");
        if (pid == 0) {
            std::vector<char*> raw_args;
            for (const auto& a : stages[0].args) raw_args.push_back(const_cast<char*>(a.c_str()));
            raw_args.push_back(nullptr);
            ::execvp(raw_args[0], raw_args.data());
            ::_exit(127);
        }
        int status = 0;
        ::waitpid(pid, &status, 0);
        return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    }

    // Створюємо канали із прапорцем O_CLOEXEC
    struct PipeEnds {
        UniqueFd read_end;
        UniqueFd write_end;
    };
    std::vector<PipeEnds> pipes(n - 1);

    for (size_t i = 0; i < n - 1; ++i) {
        int fds[2];
        if (::pipe2(fds, O_CLOEXEC) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
        pipes[i].read_end.reset(fds[0]);
        pipes[i].write_end.reset(fds[1]);
    }

    std::vector<pid_t> pids;
    pids.reserve(n);

    for (size_t i = 0; i < n; ++i) {
        pid_t pid = ::fork();
        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }

        if (pid == 0) {
            // Дочірній процес: дублюємо вхід
            if (i > 0) {
                if (::dup2(pipes[i - 1].read_end.get(), STDIN_FILENO) < 0) {
                    ::_exit(1);
                }
            }
            // Дублюємо вихід
            if (i < n - 1) {
                if (::dup2(pipes[i].write_end.get(), STDOUT_FILENO) < 0) {
                    ::_exit(1);
                }
            }

            // Закриваємо всі RAII-дескриптори каналів перед exec
            pipes.clear();

            std::vector<char*> raw_args;
            for (const auto& a : stages[i].args) {
                raw_args.push_back(const_cast<char*>(a.c_str()));
            }
            raw_args.push_back(nullptr);

            ::execvp(raw_args[0], raw_args.data());
            ::_exit(127);
        }

        pids.push_back(pid);
    }

    // Батьківський процес закриває всі свої копії каналів через очищення вектору
    pipes.clear();

    int last_status = 0;
    for (size_t i = 0; i < n; ++i) {
        int status = 0;
        ::waitpid(pids[i], &status, 0);
        if (i == n - 1 && WIFEXITED(status)) {
            last_status = WEXITSTATUS(status);
        }
    }

    return last_status;
}

int main() {
    try {
        std::vector<Stage> pipeline = {
            {{"cat", "/etc/passwd"}},
            {{"grep", "-v", "nobody"}},
            {{"cut", "-d:", "-f1"}}
        };

        return execute_pipeline(pipeline);
    } catch (const std::exception& ex) {
        std::cerr << "Pipeline error: " << ex.what() << '\n';
        return 1;
    }
}
