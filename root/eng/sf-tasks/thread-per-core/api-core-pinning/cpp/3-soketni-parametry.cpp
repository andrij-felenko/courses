#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <system_error>

namespace tpc {

/* C++ функція налаштування сокета шарду */
inline void configure_tpc_socket(int fd, int cpu_id) {
    int opt = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
        throw std::system_error(errno, std::generic_category(), "SO_REUSEPORT failed");
    }
    if (setsockopt(fd, SOL_SOCKET, SO_INCOMING_CPU, &cpu_id, sizeof(cpu_id)) < 0) {
        throw std::system_error(errno, std::generic_category(), "SO_INCOMING_CPU failed");
    }
    int nodelay = 1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        throw std::system_error(errno, std::generic_category(), "TCP_NODELAY failed");
    }
}

} // namespace tpc
