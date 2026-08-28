#include <unistd.h>
#include <vector>
#include <string>
#include <system_error>
#include <cerrno>

// Обгортка C++20 для безпечного виклику execvp з використанням RAII-контейнерів
[[noreturn]] void execute_in_path(const std::string& filename, const std::vector<std::string>& args) {
    std::vector<char*> c_argv;
    c_argv.reserve(args.size() + 1);
    for (const auto& arg : args) {
        c_argv.push_back(const_cast<char*>(arg.c_str()));
    }
    c_argv.push_back(nullptr);

    ::execvp(filename.c_str(), c_argv.data());

    // Якщо execvp повернув управління, виникла помилка
    throw std::system_error(errno, std::generic_category(), "execvp failed for " + filename);
}
