#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

int query_offloads_c(const char *ifname) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    struct ethtool_value eval;
    memset(&eval, 0, sizeof(eval));
    eval.cmd = ETHTOOL_GFLAGS;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (caddr_t)&eval;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        perror("ioctl SIOCETHTOOL");
        close(fd);
        return -1;
    }

    printf("Стан розвантажень для %s:\n", ifname);
    printf("  RX Checksum: %s\n", (eval.data & ETH_FLAG_RXCSUM) ? "Увімкнено" : "Вимкнено");
    printf("  TX Checksum: %s\n", (eval.data & ETH_FLAG_TXCSUM) ? "Увімкнено" : "Вимкнено");
    printf("  TSO:         %s\n", (eval.data & ETH_FLAG_TSO)    ? "Увімкнено" : "Вимкнено");

    close(fd);
    return 0;
}
