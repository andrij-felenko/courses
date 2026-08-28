#include <iostream>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

class SafeRedirector {
public:
    static std::error_code redirect_stdout(std::string_view filename) {
        int fd = ::open(filename.data(), O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
        if (fd < 0) {
            return std::error_code(errno, std::generic_category());
        }

        if (::dup3(fd, STDOUT_FILENO, O_CLOEXEC) < 0) {
            int err = errno;
            ::close(fd);
            return std::error_code(err, std::generic_category());
        }

        ::close(fd);
        return {};
    }
};
