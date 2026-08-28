#include <unistd.h>
#include <fcntl.h>
#include <filesystem>
#include <system_error>

void execute_via_fd(const std::filesystem::path& path, const std::vector<std::string>& args) {
    int fd = ::open(path.c_str(), O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "open failed for " + path.string());
    }
    std::vector<char*> c_argv;
    for (const auto& a : args) c_argv.push_back(const_cast<char*>(a.c_str()));
    c_argv.push_back(nullptr);

    ::fexecve(fd, c_argv.data(), environ);
    ::close(fd);
    throw std::system_error(errno, std::generic_category(), "fexecve failed");
}
