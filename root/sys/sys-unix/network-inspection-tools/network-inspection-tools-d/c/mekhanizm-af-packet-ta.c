#include <sys/socket.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <arpa/inet.h>
#include <linux/filter.h>
#include <unistd.h>

/* Відкриття сокета AF_PACKET для перехоплення всіх Ethernet-кадрів */
int open_capture_socket(struct sock_fprog *bpf_prog) {
    int fd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (fd < 0) {
        return -1;
    }

    /* Підключення програми фільтра BPF до сокета */
    if (bpf_prog != NULL) {
        if (setsockopt(fd, SOL_SOCKET, SO_ATTACH_FILTER, bpf_prog, sizeof(*bpf_prog)) < 0) {
            close(fd);
            return -1;
        }
    }
    return fd;
}
