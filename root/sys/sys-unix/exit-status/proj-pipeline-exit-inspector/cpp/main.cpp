#include <iostream>
#include <vector>
#include <string>
#include <span >
#include <memory>
#include <expected>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

// RAII-обгортка для безпечного керування файловими дескрипторами каналів
class PipeFD {
    int fd_ = -1;
public:
    explicit PipeFD(int fd = -1) : fd_(fd) {}
    ~PipeFD() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    PipeFD(const PipeFD&) = delete;
    PipeFD& operator=(const PipeFD&) = delete;

    PipeFD(PipeFD&& o) noexcept : fd_(o.fd_) {
        o.fd_ = -1;
    }

    PipeFD& operator=(PipeFD&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const { return fd_; }
    void release() { fd_ = -1; }
};

struct ProcessInfo {
    std::string command_name;
    pid_t pid;
    int exit_code;
};

class PipelineInspector {
public:
    static std::expected<std::vector<ProcessInfo>, std::string> 
    run_pipeline(std::span<const std::vector<std::string>> commands) {
        size_t n = commands.size();
        if (n == 0) return std::unexpected("Отримано порожній конвеєр");

        std::vector<std::pair<PipeFD, PipeFD>> pipes;
        pipes.reserve(n - 1);

        for (size_t i = 0; i < n - 1; ++i) {
            int fds[2];
            if (::pipe(fds) < 0) {
                return std::unexpected("Системна помилка виклику pipe()");
            }
            pipes.emplace_back(PipeFD(fds[0]), PipeFD(fds[1]));
        }

        std::vector<ProcessInfo> results;
        results.reserve(n);

        for (size_t i = 0; i < n; ++i) {
            pid_t pid = ::fork();
            if (pid < 0) {
                return std::unexpected("Системна помилка виклику fork()");
            }

            if (pid == 0) { // Child process
                if (i > 0) {
                    ::dup2(pipes[i - 1].first.get(), STDIN_FILENO);
                }
                if (i < n - 1) {
                    ::dup2(pipes[i].second.get(), STDOUT_FILENO);
                }

                // Деструктори векторів pipes автоматично закриють усі не потрібні дескриптори
                pipes.clear();

                std::vector<char*> raw_argv;
                for (const auto& arg : commands[i]) {
                    raw_argv.push_back(const_cast<char*>(arg.c_str()));
                }
                raw_argv.push_back(nullptr);

                ::execvp(raw_argv[0], raw_argv.data());
                ::_exit(127); // POSIX код помилки запускa
            }

            results.push_back({commands[i][0], pid, 0});
        }

        // Parent process очищує вектор дескрипторів
        pipes.clear();

        // Очікування завершення кожного процесa
        for (auto& proc : results) {
            int wstatus = 0;
            ::waitpid(proc.pid, &wstatus, 0);

            if (WIFEXITED(wstatus)) {
                proc.exit_code = WEXITSTATUS(wstatus);
            } else if (WIFSIGNALED(wstatus)) {
                proc.exit_code = 128 + WTERMSIG(wstatus);
            } else {
                proc.exit_code = 1;
            }
        }

        return results;
    }

    static int compute_exit_status(std::span<const ProcessInfo> results, bool pipefail) {
        if (results.empty()) return 0;

        if (pipefail) {
            for (const auto& proc : results) {
                if (proc.exit_code != 0) {
                    return proc.exit_code;
                }
            }
            return 0;
        }

        return results.back().exit_code;
    }
};

int main() {
    std::vector<std::vector<std::string>> cmds = {
        {"cat", "/dev/nonexistent_file"},
        {"grep", "main"},
        {"head", "-n", "5"}
    };

    auto res = PipelineInspector::run_pipeline(cmds);
    if (!res) {
        std::cerr << "Помилка виконання: " << res.error() << "\n";
        return 1;
    }

    std::cout << "--- Результати трасування C++20 PipelineInspector ---\n";
    for (const auto& proc : *res) {
        std::cout << "  Команда: " << proc.command_name 
                  << " | PID: " << proc.pid 
                  << " | Exit Code: " << proc.exit_code << "\n";
    }

    std::cout << "Підсумковий статус (без pipefail): " 
              << PipelineInspector::compute_exit_status(*res, false) << "\n";
    std::cout << "Підсумковий статус (з pipefail):    " 
              << PipelineInspector::compute_exit_status(*res, true) << "\n";

    return 0;
}
