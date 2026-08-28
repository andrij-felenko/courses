/* Отримання поточного кешованого PMTU мовою C */
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>

int get_socket_pmtu(int sock_fd) {
    int current_pmtu = 0;
    socklen_t len = sizeof(current_pmtu);
    if (getsockopt(sock_fd, IPPROTO_IP, IP_MTU, &current_pmtu, &len) < 0) {
        perror("getsockopt IP_MTU");
        return -1;
    }
    return current_pmtu;
}
