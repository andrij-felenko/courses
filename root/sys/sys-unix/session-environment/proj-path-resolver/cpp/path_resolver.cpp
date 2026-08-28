// path_resolver.cpp — Ідіоматична реалізація мовою C++20
#include <iostream>
#include <string>
#include <vector>
#include <string_view>
#include <unordered_map>
#include <filesystem>
#include <optional>
#include <sstream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

namespace fs = std::filesystem;

class PathResolver {
public:
    PathResolver() {
        const char* path_env = std::getenv("PATH");
        std::string_view path_str = path_env ? path_env : "/usr/bin:/bin";
        
        std::stringstream ss{std::string(path_str)};
        std::string item;
        while (std::getline(ss, item, ':')) {
            search_paths_.push_back(item.empty() ? fs::path(".") : fs::path(item));
        }
    }

    std::optional<fs::path> resolve(std::string_view cmd) {
        if (cmd.find('/') != std::string_view::npos) {
            return fs::path(cmd);
        }

        std::string cmd_key(cmd);
        if (auto it = cache_.find(cmd_key); it != cache_.end()) {
            std::cout << "[DEBUG C++ Cache HIT] " << cmd << " -> " << it->second << "\n";
            return it->second;
        }

        for (const auto& dir : search_paths_) {
            fs::path candidate = dir / cmd;
            std::error_code ec;
            if (fs::is_regular_file(candidate, ec) &&
                ::faccessat(AT_FDCWD, candidate.c_str(), X_OK, AT_EACCESS) == 0) {
                std::cout << "[DEBUG C++ PATH Found] " << cmd << " -> " << candidate << "\n";
                cache_[cmd_key] = candidate;
                return candidate;
            }
        }
        return std::nullopt;
    }

private:
    std::vector<fs::path> search_paths_;
    std::unordered_map<std::string, fs::path> cache_;
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <команда> [аргументи...]\n";
        return 1;
    }

    PathResolver resolver;
    std::string_view cmd_name = argv[1];

    auto resolved = resolver.resolve(cmd_name);
    if (!resolved) {
        std::cerr << "Помилка: команду '" << cmd_name << "' не знайдено у PATH\n";
        return 127;
    }

    std::vector<char*> c_argv;
    c_argv.reserve(argc);
    for (int i = 1; i < argc; ++i) {
        c_argv.push_back(argv[i]);
    }
    c_argv.push_back(nullptr);

    pid_t pid = ::fork();
    if (pid == 0) {
        ::execv(resolved->c_str(), c_argv.data());
        std::perror("execv failed");
        std::exit(127);
    } else if (pid > 0) {
        int status = 0;
        ::waitpid(pid, &status, 0);
        std::cout << "[Child process exited with status " << WEXITSTATUS(status) << "]\n";
    }

    return 0;
}
