#include <iostream>
#include <vector>
#include <string>
#include <array>
#include <memory>
#include <system_error>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>

class ScopedPipe {
public:
    ScopedPipe() {
        if (::pipe2(fds_.data(), O_CLOEXEC) == -1) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
    }

    ~ScopedPipe() {
        close_read();
        close_write();
    }

    ScopedPipe(const ScopedPipe&) = delete;
    ScopedPipe& operator=(const ScopedPipe&) = delete;

    ScopedPipe(ScopedPipe&& other) noexcept : fds_(other.fds_) {
        other.fds_ = {-1, -1};
    }

    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }

    void close_read() noexcept {
        if (fds_[0] != -1) {
            ::close(fds_[0]);
            fds_[0] = -1;
        }
    }

    void close_write() noexcept {
        if (fds_[1] != -1) {
            ::close(fds_[1]);
            fds_[1] = -1;
        }
    }

private:
    std::array<int, 2> fds_{-1, -1};
};

struct Command {
    std::string program;
    std::vector<std::string> args;

    std::vector<char*> to_argv() const {
        std::vector<char*> argv;
        argv.push_back(const_cast<char*>(program.c_str()));
        for (const auto& arg : args) {
            argv.push_back(const_cast<char*>(arg.c_str()));
        }
        argv.push_back(nullptr);
        return argv;
    }
};

int execute_cpp_pipeline(const std::vector<Command>& commands) {
    if (commands.empty()) return 0;

    const std::size_t n = commands.size();
    std::vector<ScopedPipe> pipes;
    pipes.reserve(n - 1);
    for (std::size_t i = 0; i < n - 1; ++i) {
        pipes.emplace_back();
    }

    std::vector<pid_t> pids;
    pids.reserve(n);

    for (std::size_t i = 0; i < n; ++i) {
        pid_t pid = ::fork();
        if (pid == -1) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }

        if (pid == 0) {
            // --- ДОЧІРНІЙ ПРОЦЕС ---
            if (i > 0) {
                if (::dup2(pipes[i - 1].read_fd(), STDIN_FILENO) == -1) {
                    ::perror("dup2 stdin");
                    ::_exit(EXIT_FAILURE);
                }
            }

            if (i < n - 1) {
                if (::dup2(pipes[i].write_fd(), STDOUT_FILENO) == -1) {
                    ::perror("dup2 stdout");
                    ::_exit(EXIT_FAILURE);
                }
            }

            // Закриваємо дескриптори каналів перед execvp
            for (auto& p : pipes) {
                p.close_read();
                p.close_write();
            }

            auto argv = commands[i].to_argv();
            ::execvp(argv[0], argv.data());
            ::perror("execvp failed");
            ::_exit(EXIT_FAILURE);
        }

        pids.push_back(pid);
    }

    // БАТЬКІВСЬКИЙ ПРОЦЕС: Закриваємо всі дескриптори каналів
    for (auto& p : pipes) {
        p.close_read();
        p.close_write();
    }

    int last_status = 0;
    for (std::size_t i = 0; i < pids.size(); ++i) {
        int status = 0;
        ::waitpid(pids[i], &status, 0);
        if (i == pids.size() - 1) {
            last_status = status;
        }
    }

    return WIFEXITED(last_status) ? WEXITSTATUS(last_status) : -1;
}

int main() {
    std::vector<Command> pipeline = {
        {"cat", {"/etc/passwd"}},
        {"grep", {"bash"}},
        {"wc", {"-l"}}
    };

    try {
        std::cout << "Executing C++ pipeline: cat /etc/passwd | grep bash | wc -l\n";
        int rc = execute_cpp_pipeline(pipeline);
        std::cout << "Pipeline finished with exit code: " << rc << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
