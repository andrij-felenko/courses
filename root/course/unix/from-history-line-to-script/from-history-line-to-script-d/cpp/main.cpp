#include <iostream>
#include <vector>
#include <string>
#include <unistd.h>
#include <system_error>

int main() {
    const std::string script_path = "/usr/local/bin/backup-tool.sh";
    
    // Формування масиву аргументів за стандартом POSIX
    std::vector<std::string> args = {
        script_path,
        "--source", "/var/www/data",
        "--dest", "/var/backups"
    };

    std::vector<std::string> env_vars = {
        "PATH=/usr/bin:/bin:/usr/local/bin",
        "LOG_LEVEL=DEBUG"
    };

    // Підготовка масивів покажчиків char* для C-інтерфейсу execve
    std::vector<char*> c_args;
    c_args.reserve(args.size() + 1);
    for (auto& arg : args) {
        c_args.push_back(arg.data());
    }
    c_args.push_back(nullptr);

    std::vector<char*> c_env;
    c_env.reserve(env_vars.size() + 1);
    for (auto& env : env_vars) {
        c_env.push_back(env.data());
    }
    c_env.push_back(nullptr);

    std::cout << "Виклик execve для запуску сценарію...\n";
    if (execve(c_args[0], c_args.data(), c_env.data()) == -1) {
        auto ec = std::error_code(errno, std::generic_category());
        std::cerr << "Помилка execve: " << ec.message() << '\n';
        return ec.value();
    }

    return 0;
}
