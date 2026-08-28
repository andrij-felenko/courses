#include <sys/socket.h>
#include <net/if.h>
#include <string.h>
#include <stdbool.h>

bool bind_socket_to_interface(int sock_fd, const char *iface_name) {
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, iface_name, sizeof(ifr.ifr_name) - 1);

    int res = setsockopt(sock_fd, SOL_SOCKET, SO_BINDTODEVICE, (const void *)&ifr, sizeof(ifr));
    return (res == 0);
}
