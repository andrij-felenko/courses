#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <expected>
#include <optional>
#include <system_error>
#include <span>

#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <cstring>

// ============================================================================
// RAII-ОБГОРТКА НАД ФАЙЛОВИМ ДЕСКРИПТОРОМ (Безпека ресурсів)
// ============================================================================
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit constexpr UniqueFd(int fd) noexcept : fd_(fd) {}
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

// ============================================================================
// ШАР 1: ПОЛІТИКА (Policy) — правила перезапуску та таймінги
// ============================================================================
struct SupervisorPolicy {
    int max_retries{3};
    std::chrono::milliseconds base_delay{200};
    std::chrono::milliseconds max_delay{2000};
    bool restart_on_clean_exit{false};
};

class PolicyEngine {
public:
    explicit PolicyEngine(SupervisorPolicy policy)
        : policy_(policy), current_delay_(policy.base_delay) {}

    [[nodiscard]] bool should_restart(int exit_status) {
        if (WIFEXITED(exit_status) && WEXITSTATUS(exit_status) == 0 && !policy_.restart_on_clean_exit) {
            std::cout << "[ПОЛІТИКА] Процес успішно завершився (exit code 0). Рестарт не потрібен.\n";
            return false;
        }

        attempts_made_++;
        if (attempts_made_ > policy_.max_retries) {
            std::cout << "[ПОЛІТИКА] Вичерпано ліміт спроб (" << policy_.max_retries << "). Зупинка.\n";
            return false;
        }

        std::cout << "[ПОЛІТИКА] Спроба " << attempts_made_ << "/" << policy_.max_retries
                  << ". Очікування " << current_delay_.count() << " мс перед рестартом...\n";

        std::this_thread::sleep_for(current_delay_);

        current_delay_ = std::min(current_delay_ * 2, policy_.max_delay);
        return true;
    }

private:
    SupervisorPolicy policy_;
    int attempts_made_{0};
    std::chrono::milliseconds current_delay_;
};

// ============================================================================
// ШАР 2: МЕХАНІЗМ (Mechanism) — запуск і взаємодія з ядром
// ============================================================================
struct ChildProcess {
    pid_t pid;
    UniqueFd log_pipe_read;
};

class ProcessRunner {
public:
    static std::expected<ChildProcess, std::error_code> spawn(std::span<char* const> args) {
        int fds[2];
        if (::pipe2(fds, O_CLOEXEC) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        UniqueFd read_end(fds[0]);
        UniqueFd write_end(fds[1]);

        pid_t pid = ::fork();
        if (pid == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (pid == 0) {
            // ДОЧІРНІЙ ПРОЦЕС
            ::setpgid(0, 0);

            if (::dup2(write_end.get(), STDOUT_FILENO) == -1 ||
                ::dup2(write_end.get(), STDERR_FILENO) == -1) {
                ::_exit(127);
            }

            read_end.reset();
            write_end.reset();

            ::execvp(args[0], args.data());
            ::_exit(127);
        }

        // БАТЬКІВСЬКИЙ ПРОЦЕС: write_end закривається автоматично RAII-деструктором
        return ChildProcess{
            .pid = pid,
            .log_pipe_read = std::move(read_end)
        };
    }

    static std::expected<int, std::error_code> collect_logs_and_wait(ChildProcess& child) {
        char buffer[256];
        ssize_t bytes_read = 0;

        while ((bytes_read = ::read(child.log_pipe_read.get(), buffer, sizeof(buffer) - 1)) > 0) {
            buffer[bytes_read] = '\0';
            std::cout << "[ЛОГ НАЩАДКА " << child.pid << "] " << buffer;
            if (buffer[bytes_read - 1] != '\n') {
                std::cout << '\n';
            }
        }

        child.log_pipe_read.reset();

        int status = 0;
        while (::waitpid(child.pid, &status, 0) == -1) {
            if (errno == EINTR) continue;
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return status;
    }
};

// ============================================================================
// ТОЧКА ВХОДУ: композиція
// ============================================================================
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <команда> [аргументи...]\n";
        return 1;
    }

    PolicyEngine policy_engine(SupervisorPolicy{
        .max_retries = 3,
        .base_delay = std::chrono::milliseconds(200),
        .max_delay = std::chrono::milliseconds(2000),
        .restart_on_clean_exit = false
    });

    std::vector<char*> target_args(&argv[1], &argv[argc]);
    target_args.push_back(nullptr);

    while (true) {
        std::cout << "\n[НАГЛЯДАЧ] Запуск: " << target_args[0] << "\n";
        auto spawn_res = ProcessRunner::spawn(std::span<char* const>(target_args.data(), target_args.size() - 1));
        if (!spawn_res) {
            std::cerr << "[НАГЛЯДАЧ] Помилка запуску: " << spawn_res.error().message() << '\n';
            break;
        }

        auto wait_res = ProcessRunner::collect_logs_and_wait(*spawn_res);
        if (!wait_res) {
            std::cerr << "[НАГЛЯДАЧ] Помилка waitpid: " << wait_res.error().message() << '\n';
            break;
        }

        int status = *wait_res;
        if (WIFEXITED(status)) {
            std::cout << "[МЕХАНІЗМ] Код завершення: " << WEXITSTATUS(status) << '\n';
        } else if (WIFSIGNALED(status)) {
            std::cout << "[МЕХАНІЗМ] Загинув від сигналу: " << WTERMSIG(status) << '\n';
        }

        if (!policy_engine.should_restart(status)) {
            break;
        }
    }

    std::cout << "[НАГЛЯДАЧ] Роботу завершено.\n";
    return 0;
}
