#include <iostream>
#include <vector>
#include <string>
#include <format>
#include <expected>
#include <unistd.h>
#include <sys/wait.h>
#include <cstring>

namespace sys {

[[nodiscard]] std::expected<int, std::string>
run_with_custom_env(const std::string& path,
                    const std::vector<std::string>& args,
                    const std::vector<std::pair<std::string, std::string>>& env_map) {
    // Формуємо рядки KEY=VALUE
    std::vector<std::string> env_strings;
    env_strings.reserve(env_map.size());
    for (const auto& [k, v] : env_map) {
        env_strings.push_back(std::format("{}={}", k, v));
    }

    // Формуємо масив покажчиків envp
    std::vector<char*> raw_envp;
    raw_envp.reserve(env_strings.size() + 1);
    for (auto& s : env_strings) {
        raw_envp.push_back(s.data());
    }
    raw_envp.push_back(nullptr);

    // Формуємо масив покажчиків argv
    std::vector<char*> raw_argv;
    raw_argv.reserve(args.size() + 2);
    std::string exec_path = path;
    raw_argv.push_back(exec_path.data());
    for (const auto& arg : args) {
        raw_argv.push_back(const_cast<char*>(arg.c_str()));
    }
    raw_argv.push_back(nullptr);

    pid_t pid = ::fork();
    if (pid < 0) {
        return std::unexpected(std::format("fork() failed: {}", std::strerror(errno)));
    }

    if (pid == 0) {
        ::execve(exec_path.c_str(), raw_argv.data(), raw_envp.data());
        std::cerr << std::format("execve failed: {}\n", std::strerror(errno));
        ::_exit(127);
    }

    int status = 0;
    if (::waitpid(pid, &status, 0) < 0) {
        return std::unexpected(std::format("waitpid() failed: {}", std::strerror(errno)));
    }

    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return std::unexpected("Process terminated abnormally");
}

} // namespace sys

int main() {
    auto res = sys::run_with_custom_env("/usr/bin/printenv", {}, {
        {"PATH", "/usr/bin:/bin"},
        {"SERVICE_PORT", "9090"},
        {"DATABASE_URL", "postgres://db.internal:5432/app"}
    });

    if (!res) {
        std::cerr << "Error: " << res.error() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
