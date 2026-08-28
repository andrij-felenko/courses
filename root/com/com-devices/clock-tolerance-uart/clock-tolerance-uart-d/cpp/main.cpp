#include <sys/ioctl.h>
#include <linux/serial.h>
#include <expected>
#include <string_view>

namespace serial_diag {

[[nodiscard]] std::expected<bool, std::string_view> hasFramingErrors(int fd) noexcept {
    serial_icounter_struct icounter{};
    if (::ioctl(fd, TIOCGICOUNT, &icounter) < 0) {
        return std::unexpected{"Failed to query serial icounter"};
    }
    return (icounter.frame > 0);
}

} // namespace serial_diag
