#include <chrono>
#include <cstring>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

class PromptProfiler {
public:
    // Метод 1: Запуск процесу через fork/execve
    static std::optional<std::string> probe_git_fork() {
        int pipefd[2];
        if (pipe(pipefd) == -1) return std::nullopt;

        pid_t pid = fork();
        if (pid == 0) {
            close(pipefd[0]);
            dup2(pipefd[1], STDOUT_FILENO);
            close(pipefd[1]);

            int devnull = open("/dev/null", O_WRONLY);
            if (devnull != -1) {
                dup2(devnull, STDERR_FILENO);
                close(devnull);
            }

            execlp("git", "git", "rev-parse", "--abbrev-ref", "HEAD", nullptr);
            _exit(127);
        }

        close(pipefd[1]);
        std::vector<char> buffer(128);
        ssize_t bytes = read(pipefd[0], buffer.data(), buffer.size() - 1);
        close(pipefd[0]);

        int status = 0;
        waitpid(pid, &status, 0);

        if (bytes > 0 && WIFEXITED(status) && WEXITSTATUS(status) == 0) {
            std::string branch(buffer.data(), bytes);
            while (!branch.empty() && (branch.back() == '\n' || branch.back() == '\r')) {
                branch.pop_back();
            }
            return branch;
        }
        return std::nullopt;
    }

    // Метод 2: Ідіоматичне пряме читання .git/HEAD
    static std::optional<std::string> probe_git_direct() {
        std::ifstream head_file(".git/HEAD");
        if (!head_file.is_open()) return std::nullopt;

        std::string line;
        if (std::getline(head_file, line)) {
            constexpr std::string_view prefix = "ref: refs/heads/";
            if (line.starts_with(prefix)) {
                return line.substr(prefix.size());
            }
            if (line.size() >= 7) {
                return line.substr(0, 7);
            }
        }
        return std::nullopt;
    }
};

int main() {
    constexpr int iterations = 1000;
    std::cout << "=== C++ Бенчмарк зондування Git (" << iterations << " ітерацій) ===\n";

    // Замір fork() + execve()
    auto t0 = std::chrono::steady_clock::now();
    for (int i = 0; i < iterations; ++i) {
        auto res = PromptProfiler::probe_git_fork();
        (void)res;
    }
    auto t1 = std::chrono::steady_clock::now();
    double us_fork = std::chrono::duration<double, std::micro>(t1 - t0).count() / iterations;

    std::cout << "1. fork() + execve(\"git\"): " << us_fork << " мкс / виклик ("
              << (us_fork / 1000.0) << " мс)\n";

    // Замір прямого читання файлу
    t0 = std::chrono::steady_clock::now();
    for (int i = 0; i < iterations; ++i) {
        auto res = PromptProfiler::probe_git_direct();
        (void)res;
    }
    t1 = std::chrono::steady_clock::now();
    double us_direct = std::chrono::duration<double, std::micro>(t1 - t0).count() / iterations;

    std::cout << "2. Пряме читання .git/HEAD:  " << us_direct << " мкс / виклик ("
              << (us_direct / 1000.0) << " мс)\n";

    std::cout << "Прискорення: " << (us_fork / us_direct) << "x\n";

    return 0;
}
