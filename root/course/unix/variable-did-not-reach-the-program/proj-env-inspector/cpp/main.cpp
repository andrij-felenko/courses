#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <filesystem>
#include <fstream>
#include <format>
#include <span>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <cstring>

namespace sys {

/* RAII-обгортка для файлового дескриптора */
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : m_fd(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }

private:
    int m_fd{-1};
};

/* Зчитування та парсинг нуль-термінованого /proc/[pid]/environ */
[[nodiscard]] std::expected<std::vector<std::string>, std::string>
read_proc_environ(pid_t pid) {
    const std::string path = std::format("/proc/{}/environ", pid);
    UniqueFd fd(::open(path.c_str(), O_RDONLY));
    if (!fd.valid()) {
        return std::unexpected(std::format("Не вдалося відкрити {}: {}", path, std::strerror(errno)));
    }

    std::vector<std::string> env_vars;
    std::vector<char> buffer(4096);
    std::string current_entry;

    while (true) {
        const ssize_t bytes = ::read(fd.get(), buffer.data(), buffer.size());
        if (bytes < 0) {
            return std::unexpected(std::format("Помилка читання {}: {}", path, std::strerror(errno)));
        }
        if (bytes == 0) {
            break;
        }

        for (ssize_t i = 0; i < bytes; ++i) {
            if (buffer[static_cast<size_t>(i)] == '\0') {
                if (!current_entry.empty()) {
                    env_vars.push_back(std::move(current_entry));
                    current_entry.clear();
                }
            } else {
                current_entry.push_back(buffer[static_cast<size_t>(i)]);
            }
        }
    }

    if (!current_entry.empty()) {
        env_vars.push_back(std::move(current_entry));
    }

    return env_vars;
}

/* Формування та виконання безпечного запуску */
class ProcessLauncher {
public:
    ProcessLauncher& add_env(std::string key, std::string value) {
        m_env_storage.push_back(std::format("{}={}", key, value));
        return *this;
    }

    [[nodiscard]] std::expected<int, std::string>
    spawn_and_inspect(std::string_view executable, const std::vector<std::string>& args) {
        // Формуємо масив покажчиків argv
        std::vector<char*> raw_argv;
        raw_argv.reserve(args.size() + 2);
        std::string exec_str(executable);
        raw_argv.push_back(exec_str.data());
        for (const auto& arg : args) {
            raw_argv.push_back(const_cast<char*>(arg.c_str()));
        }
        raw_argv.push_back(nullptr);

        // Формуємо масив покажчиків envp
        std::vector<char*> raw_envp;
        raw_envp.reserve(m_env_storage.size() + 1);
        for (auto& entry : m_env_storage) {
            raw_envp.push_back(entry.data());
        }
        raw_envp.push_back(nullptr);

        const pid_t pid = ::fork();
        if (pid < 0) {
            return std::unexpected(std::format("fork() failed: {}", std::strerror(errno)));
        }

        if (pid == 0) {
            ::execve(exec_str.c_str(), raw_argv.data(), raw_envp.data());
            std::cerr << std::format("[Дитина] execve помилка: {}\n", std::strerror(errno));
            ::_exit(127);
        }

        // Батько інспектує стан дочірнього процесу
        ::usleep(50000); // 50 мс для старту execve

        auto inspect_res = read_proc_environ(pid);
        if (inspect_res) {
            std::cout << std::format("\n=== Інспекція C++: /proc/{}/environ ===\n", pid);
            for (size_t i = 0; i < inspect_res->size(); ++i) {
                std::cout << std::format("  [{:02d}] {}\n", i + 1, (*inspect_res)[i]);
            }
            std::cout << std::format("=== Усього перевірено змінних: {} ===\n\n", inspect_res->size());
        } else {
            std::cerr << std::format("[Помилка інспекції] {}\n", inspect_res.error());
        }

        int status = 0;
        if (::waitpid(pid, &status, 0) < 0) {
            return std::unexpected(std::format("waitpid() failed: {}", std::strerror(errno)));
        }

        if (WIFEXITED(status)) {
            return WEXITSTATUS(status);
        }
        return std::unexpected("Дочірній процес завершився аномально");
    }

private:
    std::vector<std::string> m_env_storage;
};

} // namespace sys

int main() {
    std::cout << "[Лаунчер C++] Конфігурація білого списку змінних...\n";

    sys::ProcessLauncher launcher;
    launcher.add_env("PATH", "/usr/bin:/bin")
            .add_env("APP_STAGE", "staging")
            .add_env("STORAGE_BUCKET", "s3://prod-assets-data")
            .add_env("MAX_WORKERS", "16")
            .add_env("SECURITY_TOKEN", "verified_bearer_token");

    auto result = launcher.spawn_and_inspect("/bin/sleep", {"1"});
    if (!result) {
        std::cerr << std::format("[Головна помилка] {}\n", result.error());
        return EXIT_FAILURE;
    }

    std::cout << std::format("[Лаунчер C++] Запуск успішний, код виходу: {}\n", *result);
    return EXIT_SUCCESS;
}
