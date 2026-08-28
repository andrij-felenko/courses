#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

/* Налаштування сокета для Thread-per-core */
int configure_tpc_socket(int fd, int cpu_id) {
    int opt = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
        return -1;
    }
    if (setsockopt(fd, SOL_SOCKET, SO_INCOMING_CPU, &cpu_id, sizeof(cpu_id)) < 0) {
        return -1;
    }
    int nodelay = 1;
    if (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
        return -1;
    }
    return 0;
}
