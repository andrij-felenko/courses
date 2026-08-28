/* Безпечна відправка кадру без SIGPIPE у C++ */
#include <sys/socket.h>
#include <cerrno>
#include <span>
#include <system_error>

std::size_t send_safe_cpp(int fd, std::span<const std::byte> buffer) {
    const ::ssize_t res = ::send(fd, buffer.data(), buffer.size(), MSG_NOSIGNAL);
    if (res < 0) {
        if (errno == EPIPE || errno == ECONNRESET) {
            return 0; // З'єднання закрите
        }
        throw std::system_error(errno, std::generic_category(), "send failed");
    }
    return static_cast<std::size_t>(res);
}
