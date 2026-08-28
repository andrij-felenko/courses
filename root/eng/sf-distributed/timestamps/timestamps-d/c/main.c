#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/net_tstamp.h>
#include <linux/sockios.h>
#include <linux/errqueue.h>
#include <poll.h>

static int setup_hw_timestamping(int sock, const char *interface_name) {
    struct ifreq ifr;
    struct hwtstamp_config hw_cfg;

    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, interface_name, sizeof(ifr.ifr_name) - 1);

    memset(&hw_cfg, 0, sizeof(hw_cfg));
    hw_cfg.tx_type = HWTSTAMP_TX_ON;
    hw_cfg.rx_filter = HWTSTAMP_FILTER_ALL;
    ifr.ifr_data = (char *)&hw_cfg;

    if (ioctl(sock, SIOCSHWTSTAMP, &ifr) < 0) {
        perror("Попередження: SIOCSHWTSTAMP не підтримується або потрібні права root");
    }

    int flags = SOF_TIMESTAMPING_TX_HARDWARE |
                SOF_TIMESTAMPING_TX_SOFTWARE |
                SOF_TIMESTAMPING_RX_HARDWARE |
                SOF_TIMESTAMPING_RAW_HARDWARE |
                SOF_TIMESTAMPING_OPT_ID |
                SOF_TIMESTAMPING_OPT_TSONLY;

    if (setsockopt(sock, SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags)) < 0) {
        perror("Помилка: setsockopt(SO_TIMESTAMPING)");
        return -1;
    }
    return 0;
}

static void retrieve_tx_timestamp(int sock) {
    struct pollfd pfd = { .fd = sock, .events = POLLERR, .revents = 0 };
    if (poll(&pfd, 1, 1000) <= 0) {
        fprintf(stderr, "Таймаут очікування мітки в черзі помилок\n");
        return;
    }

    char ctrl_data[512];
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_control = ctrl_data;
    msg.msg_controllen = sizeof(ctrl_data);

    if (recvmsg(sock, &msg, MSG_ERRQUEUE | MSG_DONTWAIT) < 0) {
        perror("recvmsg(MSG_ERRQUEUE)");
        return;
    }

    struct cmsghdr *cmsg;
    for (cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            struct scm_timestamping *ts = (struct scm_timestamping *)CMSG_DATA(cmsg);
            printf("Зафіксовано мітку відправки (Tx):\n");
            printf("  Програмна мітка ядра: %ld.%09ld с\n",
                   (long)ts->ts[0].tv_sec, (long)ts->ts[0].tv_nsec);
            printf("  Апаратна мітка PHC:   %ld.%09ld с\n",
                   (long)ts->ts[2].tv_sec, (long)ts->ts[2].tv_nsec);
        }
    }
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "eth0";
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket()");
        return 1;
    }

    if (setup_hw_timestamping(sock, ifname) < 0) {
        close(sock);
        return 1;
    }

    struct sockaddr_in dest;
    memset(&dest, 0, sizeof(dest));
    dest.sin_family = AF_INET;
    dest.sin_port = htons(319);
    inet_pton(AF_INET, "127.0.0.1", &dest.sin_addr);

    const char packet_payload[] = "IEEE1588_SYNC_TEST_PACKET";
    ssize_t sent = sendto(sock, packet_payload, sizeof(packet_payload), 0,
                          (struct sockaddr *)&dest, sizeof(dest));
    if (sent > 0) {
        printf("Пакет надіслано (%zd байтів). Очікування апаратної мітки...\n", sent);
        retrieve_tx_timestamp(sock);
    }

    close(sock);
    return 0;
}
