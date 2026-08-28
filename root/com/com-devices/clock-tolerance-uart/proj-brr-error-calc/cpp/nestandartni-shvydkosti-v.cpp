#include <asm/termbits.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <expected>
#include <string_view>

namespace linux_uart {

[[nodiscard]] std::expected<void, std::string_view> setCustomBaudrate(int fd, unsigned int customBaud) noexcept {
    termios2 tio{};
    if (::ioctl(fd, TCGETS2, &tio) < 0) {
        return std::unexpected{"Failed to get termios2 configuration"};
    }

    tio.c_cflag &= ~CBAUD;
    tio.c_cflag |= BOTHER;
    tio.c_ispeed = customBaud;
    tio.c_ospeed = customBaud;

    if (::ioctl(fd, TCSETS2, &tio) < 0) {
        return std::unexpected{"Failed to set custom baud rate via TCSETS2"};
    }
    return {};
}

} // namespace linux_uart
