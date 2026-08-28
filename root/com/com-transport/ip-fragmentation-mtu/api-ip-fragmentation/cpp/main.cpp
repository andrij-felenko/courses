// Отримання поточного кешованого PMTU мовою C++
#include <sys/socket.h>
#include <netinet/in.h>
#include <system_error>
#include <expected>

[[nodiscard]] std::expected<int, std::error_code> get_socket_pmtu(int sock_fd) noexcept {
    int current_pmtu = 0;
    socklen_t len = sizeof(current_pmtu);
    if (::getsockopt(sock_fd, IPPROTO_IP, IP_MTU, &current_pmtu, &len) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return current_pmtu;
}
