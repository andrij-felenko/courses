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

static int enable_hwtstamp(int sock, const char *ifname) {
    struct ifreq ifr;
    struct hwtstamp_config config;

    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name) - 1);

    memset(&config, 0, sizeof(config));
    config.tx_type = HWTSTAMP_TX_ON;
    config.rx_filter = HWTSTAMP_FILTER_ALL;
    ifr.ifr_data = (char *)&config;

    if (ioctl(sock, SIOCSHWTSTAMP, &ifr) < 0) {
        perror("ioctl(SIOCSHWTSTAMP)");
        return -1;
    }
    return 0;
}

static int configure_socket_ts(int sock) {
    int flags = SOF_TIMESTAMPING_TX_HARDWARE |
                SOF_TIMESTAMPING_TX_SOFTWARE |
                SOF_TIMESTAMPING_RX_HARDWARE |
                SOF_TIMESTAMPING_RX_SOFTWARE |
                SOF_TIMESTAMPING_RAW_HARDWARE |
                SOF_TIMESTAMPING_SOFTWARE |
                SOF_TIMESTAMPING_OPT_ID |
                SOF_TIMESTAMPING_OPT_TSONLY;

    if (setsockopt(sock, SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags)) < 0) {
        perror("setsockopt(SO_TIMESTAMPING)");
        return -1;
    }
    return 0;
}

static void read_tx_timestamp(int sock) {
    struct pollfd pfd = { .fd = sock, .events = POLLERR, .revents = 0 };
    int poll_res = poll(&pfd, 1, 500); // Очікування події в черзі помилок до 500 мс

    if (poll_res <= 0) {
        fprintf(stderr, "Таймаут або помилка очікування мітки в MSG_ERRQUEUE\n");
        return;
    }

    char ctrl_buf[512];
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_control = ctrl_buf;
    msg.msg_controllen = sizeof(ctrl_buf);

    int res = recvmsg(sock, &msg, MSG_ERRQUEUE | MSG_DONTWAIT);
    if (res < 0) {
        perror("recvmsg(MSG_ERRQUEUE)");
        return;
    }

    struct cmsghdr *cmsg;
    for (cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            struct scm_timestamping *ts = (struct scm_timestamping *)CMSG_DATA(cmsg);
            printf("Отримано мітку Tx:\n");
            printf("  Програмна (SW):  %ld.%09ld с\n", (long)ts->ts[0].tv_sec, (long)ts->ts[0].tv_nsec);
            printf("  Апаратна (HW raw): %ld.%09ld с\n", (long)ts->ts[2].tv_sec, (long)ts->ts[2].tv_nsec);
        }
    }
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "eth0";
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return 1;
    }

    if (enable_hwtstamp(sock, ifname) < 0) {
        fprintf(stderr, "Попередження: Не вдалося активувати апаратне фіксування на %s\n", ifname);
    }

    if (configure_socket_ts(sock) < 0) {
        close(sock);
        return 1;
    }

    struct sockaddr_in dest_addr;
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(12345);
    inet_pton(AF_INET, "127.0.0.1", &dest_addr.sin_addr);

    const char payload[] = "Синхронізаційний тестовий пакет";
    ssize_t sent = sendto(sock, payload, sizeof(payload), 0,
                          (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (sent < 0) {
        perror("sendto");
    } else {
        printf("Пакет надіслано (%zd байтів). Очікування Tx-мітки...\n", sent);
        read_tx_timestamp(sock);
    }

    close(sock);
    return 0;
}
