#include <unistd.h>
#include <fcntl.h>
#include <cerrno>
#include <expected>
#include <system_error>

// Стандартний кросплатформний C++ еквівалент через лямбда-функцію без розширень GCC
template <typename F>
auto retry_expression(F&& f) -> decltype(f()) {
    decltype(f()) res;
    do {
        res = f();
    } while (res == -1 && errno == EINTR);
    return res;
}

std::expected<int, std::error_code> open_file_safe(const char *path) {
    int fd = retry_expression([&]() {
        return ::open(path, O_RDONLY | O_CLOEXEC);
    });
    if (fd == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return fd;
}
