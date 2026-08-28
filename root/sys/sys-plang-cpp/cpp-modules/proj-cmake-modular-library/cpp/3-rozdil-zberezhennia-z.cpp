module; // Початок глобального фрагмента модуля

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

export module matrix:storage;

import :types;
import <string_view>;
import <system_error>;

export namespace math {

[[nodiscard]] std::error_code save_to_binary_file(std::string_view path, const Matrix2x2& m) noexcept {
    int fd = ::open(path.data(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        return std::error_code(errno, std::generic_category());
    }

    ssize_t written = ::write(fd, m.data.data(), sizeof(double) * 4);
    ::close(fd);

    if (written != sizeof(double) * 4) {
        return std::make_error_code(std::errc::io_error);
    }
    return {};
}

} // namespace math
