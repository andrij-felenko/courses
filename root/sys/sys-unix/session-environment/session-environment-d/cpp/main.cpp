#include <unistd.h>
#include <vector>
#include <string>

// Виклик execvp у стилі C++20 з використанням вектора рядків
[[noreturn]] void execvp_cpp(const std::string& file, const std::vector<std::string>& args) {
    std::vector<char*> c_argv;
    c_argv.reserve(args.size() + 1);
    for (const auto& arg : args) {
        c_argv.push_back(const_cast<char*>(arg.c_str()));
    }
    c_argv.push_back(nullptr);
    ::execvp(file.c_str(), c_argv.data());
    throw std::system_error(errno, std::generic_category(), "execvp failed");
}
