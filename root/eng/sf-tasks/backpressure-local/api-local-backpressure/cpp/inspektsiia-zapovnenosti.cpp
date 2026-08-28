#include <sys/ioctl.h>
#include <linux/sockios.h>
#include <unistd.h>
#include <expected>
#include <system_error>

struct SocketQueueDepth {
    int rx_bytes{0}; // Непрочитані байти у вхідному буфері
    int tx_bytes{0}; // Ненадіслані байти у вихідному буфері
};

// Безпечне отримання глибини черг сокета засобами C++
std::expected<SocketQueueDepth, std::error_code> get_socket_queue_depth(int sock_fd) {
    SocketQueueDepth depth{};
    if (::ioctl(sock_fd, FIONREAD, &depth.rx_bytes) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::ioctl(sock_fd, SIOCOUTQ, &depth.tx_bytes) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return depth;
}
