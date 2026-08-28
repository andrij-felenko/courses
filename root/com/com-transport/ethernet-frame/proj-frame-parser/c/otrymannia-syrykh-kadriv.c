#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>

int open_raw_ethernet_socket(const char *ifname) {
    /* Відкриваємо сирий сокет для всіх канальних протоколів (ETH_P_ALL) */
    int fd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (fd < 0)
        return -1;

    /* Знаходимо числовий індекс мережевого інтерфейсу */
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name) - 1);
    if (ioctl(fd, SIOCGIFINDEX, &ifr) < 0) {
        close(fd);
        return -2;
    }

    /* Прив'язуємо сокет виключно до цього інтерфейсу */
    struct sockaddr_ll sll;
    memset(&sll, 0, sizeof(sll));
    sll.sll_family = AF_PACKET;
    sll.sll_ifindex = ifr.ifr_ifindex;
    sll.sll_protocol = htons(ETH_P_ALL);

    if (bind(fd, (struct sockaddr *)&sll, sizeof(sll)) < 0) {
        close(fd);
        return -3;
    }

    return fd;
}
