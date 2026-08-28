#include <linux/seccomp.h>
#include <sys/ioctl.h>
#include <expected>
#include <system_error>

namespace sys {

struct UserNotificationHandler {
    static std::expected<::seccomp_notif, std::error_code> receive_notif(int listener_fd) noexcept {
        ::seccomp_notif req{};
        if (::ioctl(listener_fd, SECCOMP_IOCTL_NOTIF_RECV, &req) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return req;
    }

    static std::expected<void, std::error_code> send_response(
        int listener_fd, 
        const ::seccomp_notif_resp& resp) noexcept 
    {
        if (::ioctl(listener_fd, SECCOMP_IOCTL_NOTIF_SEND, &resp) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
};

} // namespace sys
