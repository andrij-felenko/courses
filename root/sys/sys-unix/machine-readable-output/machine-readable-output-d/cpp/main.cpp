// C++20 еквівалент перевірки дескриптора через POSIX ioctl
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <cerrno>
#include <expected>

enum class DescriptorType {
    Terminal,
    NonTerminalStream,
    Invalid
};

[[nodiscard]] std::expected<DescriptorType, int> check_descriptor_is_tty(int fd) noexcept {
    struct termios t{};
    if (ioctl(fd, TCGETS, &t) == 0) {
        return DescriptorType::Terminal;
    }
    if (errno == ENOTTY) {
        return DescriptorType::NonTerminalStream;
    }
    return std::unexpected(errno);
}
